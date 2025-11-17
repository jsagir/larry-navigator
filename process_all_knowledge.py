#!/usr/bin/env python3
"""
Comprehensive Knowledge Processor for Larry
Processes both PWS library AND Course Material folders
"""

import json
from pathlib import Path
from relationship_aware_chunker import RelationshipAwareChunker

def main():
    print("=" * 80)
    print("🎯 LARRY KNOWLEDGE BASE - COMPREHENSIVE PROCESSOR")
    print("=" * 80)

    # Configuration
    pws_library_dir = Path("/home/jsagi/pws-library")
    course_material_dir = Path("/home/jsagi/Course Material")
    output_file = Path("/home/jsagi/larry_full_knowledge_chunks.json")

    # Check directories exist
    directories_to_process = []

    if pws_library_dir.exists():
        directories_to_process.append(("PWS Library", pws_library_dir))
        print(f"✅ Found: {pws_library_dir}")
    else:
        print(f"⚠️  Not found: {pws_library_dir}")

    if course_material_dir.exists():
        directories_to_process.append(("Course Material", course_material_dir))
        print(f"✅ Found: {course_material_dir}")
    else:
        print(f"⚠️  Not found: {course_material_dir}")

    if not directories_to_process:
        print("\n❌ No directories found to process!")
        return

    print(f"\n📂 Processing {len(directories_to_process)} directories...")
    print("=" * 80)

    # Create chunker
    chunker = RelationshipAwareChunker(
        target_words=1000,
        overlap_words=200
    )

    # Process each directory
    all_chunks = []
    stats = {}

    for dir_name, dir_path in directories_to_process:
        print(f"\n\n{'='*80}")
        print(f"📚 PROCESSING: {dir_name}")
        print(f"{'='*80}")

        chunks = chunker.process_directory(dir_path)
        all_chunks.extend(chunks)

        stats[dir_name] = {
            'chunks': len(chunks),
            'words': sum(len(chunk.content.split()) for chunk in chunks),
            'prior_art': sum(1 for chunk in chunks if chunk.is_prior_art)
        }

        print(f"\n✅ {dir_name}: Created {len(chunks)} chunks")

    # Save combined results
    print("\n" + "=" * 80)
    print("💾 SAVING COMBINED KNOWLEDGE BASE")
    print("=" * 80)

    chunk_dicts = [chunk.to_dict() for chunk in all_chunks]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunk_dicts, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved to: {output_file}")

    # Final statistics
    print("\n" + "=" * 80)
    print("📊 FINAL COMPREHENSIVE STATISTICS")
    print("=" * 80)

    total_chunks = len(all_chunks)
    total_words = sum(len(chunk.content.split()) for chunk in all_chunks)
    total_prior_art = sum(1 for chunk in all_chunks if chunk.is_prior_art)

    print(f"\n🎯 OVERALL:")
    print(f"  Total chunks: {total_chunks:,}")
    print(f"  Total words: {total_words:,}")
    print(f"  Average chunk size: {total_words/total_chunks:.0f} words")
    print(f"  Prior art chunks: {total_prior_art}")
    print(f"  Course material chunks: {total_chunks - total_prior_art}")

    print(f"\n📚 BY SOURCE:")
    for dir_name, stat in stats.items():
        print(f"\n  {dir_name}:")
        print(f"    Chunks: {stat['chunks']:,}")
        print(f"    Words: {stat['words']:,}")
        print(f"    Prior art: {stat['prior_art']}")

    # Framework and topic analysis
    print(f"\n🔧 TOP FRAMEWORKS:")
    from collections import defaultdict
    framework_counts = defaultdict(int)
    for chunk in all_chunks:
        for fw in chunk.frameworks:
            framework_counts[fw] += 1

    for fw, count in sorted(framework_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {fw}: {count} mentions")

    # Topic clusters
    print(f"\n🏷️  TOPIC CLUSTERS:")
    cluster_counts = defaultdict(int)
    for chunk in all_chunks:
        if chunk.relationships.topic_cluster:
            cluster_counts[chunk.relationships.topic_cluster] += 1

    for cluster, count in sorted(cluster_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cluster}: {count} chunks")

    print("\n" + "=" * 80)
    print("✅ COMPREHENSIVE KNOWLEDGE PROCESSING COMPLETE!")
    print("=" * 80)
    print(f"\n📁 Output: {output_file}")
    print(f"🎯 Larry now has {total_chunks:,} knowledge chunks ready for File Search!")
    print("\n")

if __name__ == "__main__":
    main()
