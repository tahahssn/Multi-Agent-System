from agents import search_agent, scrape_agent, writer_chain, critic_chain


def research_pipeline(topic, on_step=None):
    state = {}

    def done(i):
        if on_step:
            on_step(i, state)

    # step 1 - search agent
    res = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = res["messages"][-1].content
    done(1)

    # step 2 - reader agent
    res = scrape_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}")]
    })
    state["scrape_results"] = res["messages"][-1].content
    done(2)

    # step 3 - writer chain
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scrape_results']}"
    )
    state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
    done(3)

    # step 4 - critic chain
    state["feedback"] = critic_chain.invoke({"report": state["report"]})
    done(4)

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    out = research_pipeline(topic)
    print(out["report"], "\n", out["feedback"])