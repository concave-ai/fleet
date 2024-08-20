# Concave Fleet，大幅提升问题定位准确性。

## Concave Fleet 是 Concave project 中的实验验证性项目

Fleet 使用 Concave 提供的工具集，只在一个星期内完成了 SWE-Bench Verify 测试集的测试。
我们通过 Concave，创新性的自顶向下逐层搜索，通过多个层次的推理，逐步锁定问题的位置。

尽管最终结果还在进行最后的验证中。但是我们当前已验证的数据结果表明

- Fleet 在 SWE-Bench Verify 数据集中，问题定位准确性有大幅提升。
- Fleet 在 SWE-Bench Lite 数据集中，问题定位准确性有明显提升。

## Background

SWE Bench Verify 数据集是由 OpenAI 牵头，从头 SWE-Bench 中 筛选 一个大型的、高质量的、真实的、人工筛选标记过的软件错误定位数据集。
他使用 python 知名开源库 （如 Django， PyTest 等）的真实 issue 和 PR 作为数据集。 输入是问题的描述（基于 issue 内容），输出应当是
可以fix 该问题的 git patch。
通过 Test Case 的执行，可以验证该 patch 是否有效。

SWE-Bench Lite 数据集是 SWE-Bench 的一个子集，和 Verify 是平行关系，和 Verify 相比，筛选的规则不同，只是根据最后的文件修改是否是单文件等指标
进行筛选。问题的难易程度变化较大。

## 结论

我们通过 Fleet，发现使用 Concave 比现有的开源工具，例如 swe-agent, moatless, agentless，准确性都有明显提升。
和闭源方案，例如 GRU 相比，我们的准确性也有提升。

我们将 swe bench 中的问题定位的准确性带到新高度。

我们认为 解决率 = 问题定位准确性 * patch 生成成功率。

通过提高问题的定位准确性，我们预期可以同比提高问题的解决率

> 尽管榜单上有 CodeStory Aide/ Amazon Q 等更高分的闭源方案，但是他们没有提供 Trajs，只提供了最终结果，我们无法分析他们的推理中是如何进行问题锁定的。
> 所以我们比对了提供了 Trajs 的方案。

## 评估规则

input： issue_description, 来源于数据集
output: 为了解决问题，我们应该修改哪个文件，和哪个文件的哪部分。为了评估，我们把代码部分定义成 symbol，例如一个函数，一个
class。

已有提供了 Trajs 的方案，我们通过分析 trajs 中 产生的问题 patch，从而知道问题定位到了哪个文件，哪个函数。
对于 Fleet，我们会生成 issue_identify.json， 在其中会包括我们的问题定位结果（文件和 symbol）。

## 评估结果

swe-bench verified 数据集

| Case ID                 |         | Fleet           | swe-agent  Claude 3 Opus | swe-agent  GPT-4 | swe-agent  Claude 3.5 Sonnect |
|-------------------------|---------|-----------------|--------------------------|------------------|-------------------------------|
| **resovled Accuracy** : |         |
|                         | Total   | WIP...          | ️   18.2%	               | 	33.6%           | 22.4%                         |
|                         | PyTest  | **58%[11/19]**  | 21% [4/19]               | 	26% [5/19]	     | 36% [7/19]                    |
| Identify:               |
|                         | file    | **89% [17/19]** | 42%[8/19]                | 47%[9/19]        | 63% [12/19]                   |
|                         | symbols | **78% [15/19]** | 21%[4/19]                | 42%[8/19]        | 36%[7/19]                     |

## 原理介绍

我们主要参考 moatless. 对 moatless 的问题定位过程进行全方位的改造。

Moatless 的定位流程是

```
问题 -> SearchCode -> IdentifyCode -> DecideRelevance -> `GeneratePatch Step`
                                         need more info
           +   <-------  <-------   <------- +                              
```   

但我们发现，只给予问题作为 context 的情况下，LLM 只能片面的进行代码搜索。
虽然可以通过多轮搜索来增加 context，提高准确性，但任何一轮搜索LLM 发生错误，都会导致最终的定位失败。

因此，我们强化了代码搜索阶段，使用 静态分析+ 向量搜索，选择更多相关的context，让 LLM 进行更准确的代码搜索。

我们的具体流程是

1. 静态分析，得到 token 集合，这是由 class，function, variables 名称组成的。
2. Agent 基于tokens，选择 前十个最相关的 tokens，作为 keywords
3. 使用 keywords 进行全文搜索，返回 keyword 出现在哪些文件中。
4. 文件搜索 LLM 基于 keyword 出现的文件，进行分析，选择哪些文件是潜在相关的。
5. 对于每个潜在文件，逐一分析，回答 1. 该问题是否和问题相关 2. 如果相关，哪些 symbol 是和问题相关的。
6. 使用 vector search, 通过 keywords 和 issue 生成 5 个问题，然后搜索已经将代码片段索引好的 vector 数据库，找到最相关的代码片段。
6. 汇总所有的文件评估结果与代码片段，进行最终的汇总评估。

我们在只做一次该流程的情况下，就远超多轮搜索的 moatless /swe-agent 的准确性。

## 评估详情

| Case ID | Fleet | swe-agent Claude 3 Opus | swe-agent  GPT-4 | swe-agent  Claude 3.5 Sonnect |
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


复现 Verified 数据集:
- [Concave Fleet 运行 Log: https://github.com/concave-ai/fleet/tree/main/bench](https://github.com/concave-ai/fleet/tree/main/bench)
- swe-agent Claude 3 Opus TraJS https://github.com/swe-bench/experiments/tree/main/evaluation/verified/20240402_sweagent_claude3opus/trajs
- swe-agent GPT-4 TraJS https://github.com/swe-bench/experiments/tree/main/evaluation/verified/20240402_sweagent_gpt4/trajs
- swe-agent Claude 3.5 Sonnect TraJS https://github.com/swe-bench/experiments/tree/main/evaluation/verified/20240620_sweagent_claude3.5sonnet/trajs

## SWE bench Lite 数据集

我们的成果在 Lite 数据集上也有提升，但收到数据集质量限制，提升幅度没有 verified 数据集明显。

> Lite 数据集的缺陷和不足请参考: https://openai.com/index/introducing-swe-bench-verified/

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



## Reference


```


