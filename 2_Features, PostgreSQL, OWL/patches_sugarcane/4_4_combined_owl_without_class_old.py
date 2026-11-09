import os
import re
import psutil
from collections import defaultdict
import time
from pathlib import Path

from pipeline_config import get_config

# ============================================================
# Load config
# ============================================================
cfg = get_config()

INPUT_DIRECTORY = cfg["owl_output_dir"]
OUTPUT_FILE     = cfg["combined_owl_output"]
BASE_URI        = cfg["base_uri"]

print(f"▶ Active dataset : {cfg['active_dataset']}")
print(f"▶ Input dir      : {INPUT_DIRECTORY}")
print(f"▶ Output file    : {OUTPUT_FILE}")
print(f"▶ Base URI       : {BASE_URI}")


# ============================================================
# System helpers
# ============================================================

def get_optimal_settings():
    try:
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        cpu_count           = psutil.cpu_count()
    except Exception:
        available_memory_gb = 8.0
        cpu_count           = 4

    if available_memory_gb > 16:
        batch_size, progress_interval = 2000, 200
    elif available_memory_gb > 8:
        batch_size, progress_interval = 1000, 100
    elif available_memory_gb > 4:
        batch_size, progress_interval = 500, 50
    else:
        batch_size, progress_interval = 250, 25

    return {
        'batch_size': batch_size,
        'progress_interval': progress_interval,
        'memory_gb': available_memory_gb,
        'cpu_count': cpu_count,
    }


def auto_detect_dataset_scale(input_directory):
    print(f"🔍 Analyzing dataset scale...")
    owl_files   = list(Path(input_directory).rglob('*.owl'))
    total_files = len(owl_files)
    if total_files == 0:
        return None

    sample_files   = owl_files[:min(10, total_files)]
    total_classes  = set()
    total_props    = set()
    avg_file_size  = 0

    for file_path in sample_files:
        try:
            avg_file_size += file_path.stat().st_size
            content = file_path.read_text(encoding='utf-8')
            total_classes.update(re.findall(r':([\w]+) rdf:type owl:Class', content))
            total_props.update(re.findall(r':([\w]+) rdf:type owl:ObjectProperty', content))
        except Exception:
            continue

    avg_file_size /= len(sample_files) if sample_files else 1

    scale_info = {
        'total_files': total_files,
        'estimated_classes': len(total_classes),
        'estimated_properties': len(total_props),
        'estimated_size_mb': (total_files * avg_file_size) / (1024 * 1024),
        'avg_file_size_kb': avg_file_size / 1024,
    }

    print(f"📊 Dataset scale detected:")
    print(f"   📁 Total files              : {total_files:,}")
    print(f"   🏷️  Estimated unique classes : {scale_info['estimated_classes']:,}")
    print(f"   🔗 Estimated unique props   : {scale_info['estimated_properties']:,}")
    print(f"   💾 Estimated total size     : {scale_info['estimated_size_mb']:.1f} MB")
    print(f"   📄 Average file size        : {scale_info['avg_file_size_kb']:.1f} KB")
    return scale_info


# ============================================================
# OWL extraction
# ============================================================

def extract_owl_data_adaptive(file_path):
    """
    Extract OWL data from a single file.

    Individual names (derived from filename) may contain hyphens, dots, and
    spaces that are NOT valid Turtle local names, so they are written as
    full URIs in the combined output.
    """
    try:
        content         = Path(file_path).read_text(encoding='utf-8')
        individual_name = Path(file_path).stem  # strip .owl

        # Classes
        classes = set()
        for pattern in [r':([\w]+) rdf:type owl:Class', r':([\w]+) a owl:Class']:
            for cls in re.findall(pattern, content):
                if cls.lower() != 'image':
                    classes.add(cls)

        # Bin subclass relationships
        bin_classes = defaultdict(set)
        for pattern in [
            r':([\w]+) rdf:type owl:Class ; rdfs:subClassOf :([\w]+)',
            r':([\w]+) a owl:Class ; rdfs:subClassOf :([\w]+)',
        ]:
            for bin_cls, parent_cls in re.findall(pattern, content):
                bin_classes[parent_cls].add(bin_cls)

        # Object properties
        properties = set()
        for pattern in [r':([\w]+) rdf:type owl:ObjectProperty', r':([\w]+) a owl:ObjectProperty']:
            properties.update(re.findall(pattern, content))

        # Feature assignments
        escaped            = re.escape(individual_name)
        assignment_pattern = (
            rf':{escaped} :([\w]+) :([\w]+) \.'
            rf'\s*:([\w]+) rdf:type :([\w]+) \.'
        )
        feature_assignments = []
        for prop, instance, _instance2, bin_class in re.findall(
            assignment_pattern, content, re.MULTILINE
        ):
            feature_assignments.append({
                'property':  prop,
                'instance':  instance,
                'bin_class': bin_class,
            })

        if not feature_assignments:
            return None

        return {
            'classes':     classes,
            'bin_classes': bin_classes,
            'properties':  properties,
            'individual':  {
                'name':     individual_name,
                'features': feature_assignments,
            },
        }

    except Exception:
        return None


# ============================================================
# OWL generation
# ============================================================

def generate_combined_owl(all_classes, all_bin_classes, all_properties, individuals_data):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:

        f.write(f"""@prefix : <{BASE_URI}#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <{BASE_URI}> .

<{BASE_URI}> rdf:type owl:Ontology .

###  AUTOMATICALLY GENERATED COMBINED ONTOLOGY
###  Dataset   : {cfg['active_dataset']}
###  Generated : {time.strftime('%Y-%m-%d %H:%M:%S')}
###  Source files : {len(individuals_data):,}
###  Classes      : {len(all_classes):,}
###  Properties   : {len(all_properties):,}
###  Individuals  : {len(individuals_data):,}

#################
### Classes
#################

:Image rdf:type owl:Class .

""")

        print(f"  ✍️  Writing {len(all_classes):,} classes...")
        algorithm_groups = defaultdict(list)
        for cls in all_classes:
            parts = cls.split('_', 1)
            algorithm_groups[parts[0] if len(parts) > 1 else 'Other'].append(cls)

        for algorithm in sorted(algorithm_groups.keys()):
            readable = algorithm.replace('Textures', ' Textures').replace('Histogram', ' Histogram')
            f.write(f"# {readable} Features\n")
            for cls in sorted(algorithm_groups[algorithm]):
                f.write(f":{cls} rdf:type owl:Class .\n")
                if cls in all_bin_classes:
                    for bin_cls in sorted(all_bin_classes[cls]):
                        f.write(f":{bin_cls} rdf:type owl:Class ; rdfs:subClassOf :{cls} .\n")
                    f.write("\n")

        print(f"  ✍️  Writing {len(all_properties):,} properties...")
        f.write("#################\n### Object Properties\n#################\n\n")
        for prop in sorted(all_properties):
            if prop.startswith('has'):
                range_cls = prop[3:]
                if range_cls in all_classes:
                    f.write(
                        f":{prop} rdf:type owl:ObjectProperty ; "
                        f"rdfs:domain :Image ; rdfs:range :{range_cls} .\n"
                    )

        print(f"  ✍️  Writing {len(individuals_data):,} individuals...")
        f.write("\n#################\n### Individuals\n#################\n\n")

        for individual in individuals_data:
            name = individual['name']
            uri  = f"<{BASE_URI}#{name}>"

            f.write(f"{uri} rdf:type :Image .\n\n")
            for feat in individual['features']:
                f.write(f"{uri} :{feat['property']} :{feat['instance']} .\n")
                f.write(f":{feat['instance']} rdf:type :{feat['bin_class']} .\n\n")


# ============================================================
# Main
# ============================================================

def combine_owl_files():
    print(f"🚀 Starting OWL file combination...")

    if not os.path.exists(INPUT_DIRECTORY):
        print(f"❌ Input directory does not exist: {INPUT_DIRECTORY}")
        input("Press Enter to exit...")
        return

    system_settings = get_optimal_settings()
    print(f"💻 System resources detected:")
    print(f"   🧠 Available memory : {system_settings['memory_gb']:.1f} GB")
    print(f"   ⚡ CPU cores        : {system_settings['cpu_count']}")
    print(f"   📦 Batch size       : {system_settings['batch_size']:,}")

    scale_info = auto_detect_dataset_scale(INPUT_DIRECTORY)
    if not scale_info:
        print("❌ No OWL files found in the input directory!")
        input("Press Enter to exit...")
        return

    start_time = time.time()

    all_classes      = set()
    all_bin_classes  = defaultdict(set)
    all_properties   = set()
    individuals_data = []

    owl_files   = list(Path(INPUT_DIRECTORY).rglob('*.owl'))
    total_files = len(owl_files)
    print(f"🔄 Processing {total_files:,} files...")

    processed_count = 0
    failed_count    = 0

    for i, file_path in enumerate(owl_files):
        try:
            data = extract_owl_data_adaptive(str(file_path))
            if data:
                all_classes.update(data['classes'])
                for parent, bins in data['bin_classes'].items():
                    all_bin_classes[parent].update(bins)
                all_properties.update(data['properties'])
                individuals_data.append(data['individual'])
                processed_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
            if failed_count <= 5:
                print(f"⚠️  Error processing {file_path.name}: {e}")

        if (i + 1) % 100 == 0:
            elapsed = time.time() - start_time
            rate    = (i + 1) / elapsed if elapsed > 0 else 0
            eta     = (total_files - i - 1) / rate if rate > 0 else 0
            print(
                f"📈 Progress: {i+1:,}/{total_files:,} "
                f"({(i+1)/total_files*100:.1f}%) | "
                f"Rate: {rate:.1f}/sec | ETA: {eta:.0f}s"
            )

    print(f"\n✅ Processing complete!")
    print(f"   ✅ Successfully processed : {processed_count:,}/{total_files:,}")
    print(f"   ❌ Failed files           : {failed_count:,}")
    print(f"   🏷️  Unique classes         : {len(all_classes):,}")
    print(f"   📦 Unique bin classes     : {sum(len(b) for b in all_bin_classes.values()):,}")
    print(f"   🔗 Unique properties      : {len(all_properties):,}")
    print(f"   👤 Total individuals      : {len(individuals_data):,}")

    print(f"\n📝 Generating combined OWL file...")
    generate_combined_owl(all_classes, all_bin_classes, all_properties, individuals_data)

    total_time = time.time() - start_time
    print(f"\n🎉 Combination complete!")
    print(f"⏱️  Total time      : {total_time:.2f} seconds")
    print(f"⚡ Processing rate : {total_files/total_time:.1f} files/second")

    if os.path.exists(OUTPUT_FILE):
        file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
        print(f"📏 Output size     : {file_size_mb:.2f} MB")
        print(f"📁 Output location : {OUTPUT_FILE}")
    else:
        print(f"❌ Output file was not created!")

    print(f"\n🚀 Ready for concept induction with ECII or DL-Learner!")
    input("Press Enter to exit...")


if __name__ == "__main__":
    print("=" * 60)
    print("    🦉 OWL FILE COMBINER")
    print("    Combining individual OWL files into one dataset")
    print("=" * 60)
    print()
    try:
        combine_owl_files()
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
