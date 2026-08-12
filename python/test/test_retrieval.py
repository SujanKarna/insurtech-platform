from retrieval.retriever import Retriever


def main():

    query = "Was ist ein Unfall?"

    retriever = Retriever()

    results = retriever.retrieve(
        query=query,
        top_k=5,
    )

    print("=" * 90)
    print(f"QUERY: {query}")
    print("=" * 90)

    for index, result in enumerate(results, start=1):

        print(f"\n[{index}]")
        print(f"Score   : {result.score:.4f}")
        print(f"Chunk   : {result.chunk_id}")
        print(f"Section : {result.section_number}")
        print(f"Title   : {result.section_title}")
        print(
            f"Pages   : "
            f"{result.page_start}-{result.page_end}"
        )

        print("Path:")
        for section in result.section_path:
            print(f"  → {section}")

        print("\nText:")
        print(result.text)

        print("-" * 90)


if __name__ == "__main__":
    main()