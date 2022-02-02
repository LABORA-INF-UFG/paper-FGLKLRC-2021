
# PlaceRAN: optimal placement of virtualized network functions in Beyond 5G radio access networks

This repository aims to demonstrate the **PlaceRAN: optimal placement of virtualized network functions in Beyond 5G radio access networks** model implementation.  In our tests we used the Ubuntu Server 18.04 and Ubuntu 20.04, with Python 3.6.9, docplex 2.20.204 and the IBM CPLEX version 12.8.0.

- [Description](#description)
- [Topologies](#topologies)
- [Scenarios](#scenarios)
- [Final Results](#final-results)
- [Citation](#citation)

## Description
This work proposes the first exact model for positioning radio functions for vNGRAN planning, named **PlaceRAN**, as a *Mixed-Integer Linear Programming (MILP)* problem. The objective is to minimize the computing resources and maximize the aggregation level of radio functions. The evaluation considered two realistic network topologies, named as T1 and T2. 

This repository contains more informations about our model, the T1 and T2 topologies, the scenarios and about our final results.

## Topologies
In our evaluation we used two topologies, named Topology 1 (T1) and Topology 2 (T2) to compare the different topology scenarios (Low Quality, Random Quality and High Quality) and RUs scenarios (F1 and R1). 

T1 topology represents a current ring based RAN deployment, with two CRs positioned close to the core network, in a centralized way, and the others 49 CRs are distributed as a ring based cluster. 

The T2 topology is a hierarchical topology, that are organized in layers, this kind of topologies shows a trend in the design of the future RAN topologies, being aligned with the most recent analysis. T2 topology has two CRs positioned close to the core network, in a centralized way, and the others 126 CRs are distributed in hierarchical layers.


<p align="center">
  <img src="https://github.com/LABORA-INF-UFG/paper-FGLKLRC-2021/blob/main/topo_fig.png"/>
</p>

## Scenarios

To evaluate our goals with different scenarios of topologies and radio distribution, we defined three types of topology scenarios named as High Capacity (HC), Random Capacity (RC) and Low Capacity (LC). The HC scenario have high quality links with higher bandwidth and lower latency values. The LC scenario is the opposite, links with lower bandwidth and higher latency values. Finally, the RC scenario is the middle ground between the HC and LC scenarios, with links having higher and lower bandwidth and latency values.

We also define different scenarios to the Radio Units (RUs) distribution named as Fixed 1 (F1) and Random 1 (R1). In the F1 scenario, each CR has a RU coupled to it. In the R1 scenario, we define the RU distribution randomly, where each CR can have one RU coupled to it or none.

## Final results

To see the final results, i. e., the optimal solutions of each topology and/or the improvements of each scenario, we provide a set of charts that can be used to compare the improvements of our approach. The topology files, scenarios and the model implementation are in this repository.

## Citation

```
@article{DBLP:journals/corr/abs-2102-13192,
  author    = {Fernando Zanferrari Morais and
               Gabriel Matheus de Almeida and
               Leizer de Lima Pinto and
               Kleber Vieira Cardoso and
               Luis M. Contreras and
               Rodrigo da Rosa Righi and
               Cristiano Bonato Both},
  title     = {PlaceRAN: Optimal Placement for the Virtualized Next-Generation {RAN}},
  journal   = {CoRR},
  volume    = {abs/2102.13192},
  year      = {2021},
  url       = {https://arxiv.org/abs/2102.13192},
  eprinttype = {arXiv},
  eprint    = {2102.13192},
  timestamp = {Thu, 05 Aug 2021 08:50:01 +0200},
  biburl    = {https://dblp.org/rec/journals/corr/abs-2102-13192.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```
