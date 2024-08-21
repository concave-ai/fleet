### Concave Fleet: Significantly Enhanced Issue Localization Accuracy

#### Overview

Concave Fleet is an experimental validation project within the Concave initiative. Utilizing the tools provided by Concave, Fleet completed the SWE-Bench Verify test suite in just one week, employing:
   - Concave Workspace
   - Concave Hybrid Search

Leveraging Concave, we innovatively implemented a top-down, layered search strategy. Through multi-level reasoning, we progressively narrowed down the root cause of issues.

Although the final results are still undergoing validation, preliminary data indicates the following:
- Fleet achieved substantial improvements in issue localization accuracy within the SWE-Bench Verify dataset.
- Fleet also demonstrated noticeable accuracy improvements within the SWE-Bench Lite dataset.

#### Background

The SWE-Bench Verify dataset, spearheaded by OpenAI, is a high-quality, real-world, manually curated software fault localization dataset. It utilizes real issues and pull requests from well-known Python open-source libraries (e.g., Django, PyTest). The input comprises issue descriptions (based on the content of the issue), and the output is a git patch capable of resolving the issue. The effectiveness of the patch can be validated by executing the associated test cases.

The SWE-Bench Lite dataset is a subset of SWE-Bench, parallel to Verify but filtered based on different criteria, such as whether the final file modification is single-file. This subset presents a varying level of difficulty.

#### Conclusion

Through Fleet, we observed that using Concave yields a significant improvement in localization accuracy compared to existing open-source tools like swe-agent, moatless, and agentless. Our accuracy also surpasses that of proprietary solutions such as GRU.

We have set a new benchmark in issue localization accuracy within the SWE-Bench framework.

We posit that **solution rate = issue localization accuracy * patch generation success rate.** By improving localization accuracy, we expect a proportional increase in solution rates.

> Although there are higher-scoring proprietary solutions such as CodeStory Aide and Amazon Q, they do not provide Trajs and only offer final results, making it impossible to analyze their issue localization reasoning. Therefore, we compared our results with solutions that provide Trajs.

#### Evaluation Criteria

**Input:** `issue_description` derived from the dataset.
**Output:** The file and specific code segment that should be modified to resolve the issue. For evaluation purposes, code segments are defined as symbols, such as functions or classes.

For existing solutions that provide Trajs, we analyze the patch generated from the Trajs to determine which file and function were localized. For Fleet, we generate an `issue_identify.json` file that includes our localization results (file and symbol).

#### Evaluation Results

**SWE-Bench Verified Dataset**

| Case ID                 |         | Fleet           | swe-agent Claude 3 Opus | swe-agent GPT-4 | swe-agent Claude 3.5 Sonnect |
|-------------------------|---------|-----------------|--------------------------|------------------|-------------------------------|
| **Resolved Accuracy** : |         |
|                         | Total   | WIP...          | ️18.2%	               | 33.6%           | 22.4%                         |
|                         | PyTest  | **58%[11/19]**  | 21% [4/19]               | 26% [5/19]	     | 36% [7/19]                    |
| Identify:               |
|                         | file    | **89% [17/19]** | 42%[8/19]                | 47%[9/19]        | 63% [12/19]                   |
|                         | symbols | **78% [15/19]** | 21%[4/19]                | 42%[8/19]        | 36%[7/19]                     |

#### Methodology

We substantially modified the issue localization process of moatless.

The moatless localization flow is:

```
Issue -> SearchCode -> IdentifyCode -> DecideRelevance -> `GeneratePatch Step`
                                            need more info
         +   <-------  <-------   <------- +                              
```   

However, we found that when only providing the issue as context, the LLM can only conduct superficial code searches. While multiple search iterations can enhance context and accuracy, any error in a search iteration leads to overall failure in localization.

Thus, we strengthened the code search phase using static analysis and vector search to select more relevant context, enabling the LLM to perform more accurate searches.

Our refined process is as follows:

1. Static analysis to obtain a token set, consisting of class, function, and variable names.
2. The agent selects the top ten most relevant tokens as keywords based on these tokens.
3. Full-text search using the keywords identifies the files where the keywords appear.
4. File analysis: The LLM analyzes the files where keywords appear to identify potential relevance.
5. For each potential file, it determines: 1. Is this file relevant to the issue? 2. If relevant, which symbols are associated with the issue?
6. Vector search: Based on the keywords and issue description, five questions are generated, and the vector database is searched to find the most relevant code snippets.
7. Summarize all evaluation results from the files and code snippets to generate the final assessment.

By executing this process only once, we significantly surpass the multi-round search accuracy of moatless and swe-agent.

#### Evaluation Details

| Case ID | Fleet | swe-agent Claude 3 Opus | swe-agent GPT-4 | swe-agent Claude 3.5 Sonnect |
|---------|-------|-------------------------|------------------|-------------------------------|
| 5262    | ✅     | ⚠️                      | ⚠️               | ⚠️                            |
| 5631    | ✅     | ❌                       | ❌                | ✅                             |
| 5787    | ✅     | ❌                       | ❌                | ❌                             |
| 5809    | ✅     | ✅                       | ✅                | ✅                             |
| 5840    | ✅     | ❌                       | ❌                | ❌                             |
| 6197    | ❌     | ❌                       | ❌                | ⚠️                            |
| 6202    | ✅     | ❌                       | ✅                | ✅                             |
| 7205    | ✅     | ✅                       | ✅                | ✅                             |
| 7236    | ⚠️    | ❌                       | ❌                | ❌                             |
| 7342    | ✅     | ❌                       | ❌                | ❌                             |
| 7432    | ✅     | ✅                       | ✅                | ✅                             |
| 7490    | ❌     | ❌                       | ❌                | ❌                             |
| 7521    | ✅     | ⚠️                      | ❌                | ⚠️                            |
| 7571    | ✅     | ⚠️                      | ✅                | ⚠️                            |
| 7982    | ✅     | ✅                       | ✅                | ✅                             |
| 8399    | ⚠️    | ❌                       | ❌                | ❌                             |
| 10051   | ✅     | ✅                       | ✅                | ⚠️                            |
| 10081   | ✅     | ❌                       | ✅                | ❌                             |
| 10356   | ✅     | ❌                       | ❌                | ✅                             |

**Reproducing the Verified Dataset:**
- [Concave Fleet Run Log](https://github.com/concave-ai/fleet/tree/main/bench)
- [swe-agent Claude 3 Opus TraJS](https://github.com/swe-bench/experiments/tree/main/evaluation/verified/20240402_sweagent_claude3opus/trajs)
- [swe-agent GPT-4 TraJS](https://github.com/swe-bench/experiments/tree/main/evaluation/verified/20240402_sweagent_gpt4/trajs)
- [swe-agent Claude 3.5 Sonnect TraJS](https://github.com/swe-bench/experiments/tree/main/evaluation/verified/20240620_sweagent_claude3.5sonnet/trajs)

#### SWE-Bench Lite Dataset

Our achievements also extend to the Lite dataset, although the improvement is less pronounced due to limitations in dataset quality.

> For details on the limitations and shortcomings of the Lite dataset, refer to: [OpenAI SWE-Bench Verified Introduction](https://openai.com/index/introducing-swe-bench-verified/)

|                   |                  | **Fleet** | Meatless | Gru   | Agentless | sweagnet_claude3 | sweagnet_gpt4 | sweagnet_claude3.5 |
|-------------------|------------------|-----------|----------|-------|-----------|------------------|---------------|--------------------|
| resovled Accuracy |                  |           | 26.67%   | 35.67% | 29.67%     | 11.67%            | 18.33%         | 23%                 |

| Case ID | File Path                        | Function/Method                             | **Fleet** | Meatless | Gru | Agentless | sweagnet_claude3 | sweagnet_gpt4 | sweagnet_claude3.5 |
|---------|----------------------------------|---------------------------------------------|-----------|----------|-----|-----------|------------------|---------------|--------------------|
| 5103    | assertion/rewrite.py             | AssertionRewriter#visit_Call_35()           | ✅         | ✅        | ✅   | ✅         | ⚠️               | ✅             | ✅                  |
| 5221    | _pytest/python.py                | _showfixtures_main                          | ✅         | ⚠️       | ✅   | ⚠️        | ⚠️               | ✅             | ⚠️                 |
| 5227    | _pytest/logging.py               | DEFAULT_LOG_DATA_FORMAT                     | ✅         | ✅        | ✅   | ✅         | ✅                | ✅             | ✅                  |
| 5413    | _code/code.py                    | ExceptionInfo.__str__                       | ✅         | ❌        | ❌   | ❌         | ❌                | ✅             | ✅                  |
| 5495    | _pytest/assertion/util.py        | _compare_eq_sequence                        | ✅         | ❌        | ❌   | ❌         | ❌                | ⚠️            | ⚠️                 |
| 5692    | _pytest/junitxml.py              | pytest_sessionfinish                        | ✅         | ✅        | ✅   | ✅         | ⚠️               | ✅             | ✅                  |
| 6116    | _pytest/main.py                  | pytest_addoption                            | ✅         | ✅        | ✅   | ✅         | ✅                | ✅             | ✅                  |
| 7168    | _io/saferepr.py                  | _format_repr_exception                      | ✅         | ❌        | ⚠️  | ✅         | ❌                | ❌             | ✅                  |
| 7220    | src/_pytest/nodes.py             | _repr_failure_py                            | ❌         | ❌        | ⚠️  | ⚠️        | ❌                | ❌             | ❌                  |
| 7373    | src/_pytest/mark/evaluate.py     | MarkEvaluator._istrue                       | ✅         | ✅        | ✅   | ✅         | ❌                | ✅             | ✅                  |
| 7432    | src/_pytest/skipping.py          | pytest_runtest_makereport                   | ✅         | ✅        | ✅   | ✅         | ✅                | ✅             | ✅                  |
| 7490    | src/_pytest/skipping.py          | pytest_runtest_call && evaluate_xfail marks | ✅         | ❌        | ❌   | ❌         | ❌                | ❌             | ✅                  |
| 8365    | src/_pytest/tmpdir.py            | getbasetemp                                 | ✅         | ⚠️       | ⚠️  | ⚠️        | ⚠️               | ⚠️            | ✅                  |
| 8906    | src/_pytest/python.py            | _importtestmodule                           | ❌         | ❌        | ❌   | ❌         | ❌                | ❌             | ❌                  |
| 9359    | src/_pytest/_code/source.py      | get_statement_startend2                     | ❌         | ❌        | ❌   | ❌         | ❌                | ❌             | ❌                  |
| 11143   | src/_pytest/assertion/rewrite.py | run()                                       | ✅         | ❌        | ✅   | ⚠️        | ⚠️               | ⚠️            | ✅                  |
| 11148   | src/_pytest/pathlib.py           | import_path                                 | ❌         | ❌        | ✅   | ❌         | ❌                | ❌             | ❌                  |

### Limitations
Identifying issues at the function level does not necessarily lead to a direct resolution. The correct solution might involve multiple approaches. This challenge is not unique to our experiment; it also exists in the current SWE-Bench.
The tests conducted were limited to issues within the pytest repository. (Due to time and resource constraints, the complete set of 500 tests has not yet been conducted; this document will be updated with the full results once available.)
The process of pinpointing issues at the function level was performed manually, introducing potential errors.

### Thanks
We would like to express our gratitude to the OpenAI team/SWE Team for providing the SWE-Bench Verified dataset
We also thank the SweAgent team for their valuable insights and feedback.
also thank Moatless, The idea for Concave was inspired by Moatless.
