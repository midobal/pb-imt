# Prefix-based IMT User Simulation

Given a search graph generated by [Moses](https://github.com/moses-smt/mosesdecoder), this script computes WSR and MAR following the prefix-based IMT protocol by [Barrachina et al. (2009)](#references).

## Requirements
This software is an extension of [Barrachina et al. (2009)](#references)'s original user simulation and, thus, requires their original *wg* software. Contact them to obtain a copy of their binary and/or source code.

## Search graph generation
Prior to starting the simulation, you need to generate a search graph with Moses. You can do so by doing:

```
moses -f moses.ini -i test.src -osg search_graph > test.hyp
```
where `moses` is Moses' binary file; `moses.ini` is the configuration file; `test.src` is the text to translate; `search_graph` is the file in which to store the search graph; and `test.hyp` is the file containing the translation hypothesis.

## Usage
```
simulation.sh -r reference -s search_graph -d dest_dir -w wg
```
where `reference` is the reference file of the document to translate; `search_graph` is the search graph generated at the [initial step](#search-graph-generation); `dest_dir` is the directory in which store the files; and `wg` is the path to the [wg software](#requirements).

## References
>Barrachina, S., Bender, O., Casacuberta, F., Civera, J., Cubel, E., Khadivi, S., Lagarda, A., Ney, H., Tomás, J., Vidal, E., and Vilar, J.-M. (2009). Statistical approaches to computer-assisted translation. Computational Linguistics, 35:3–28.
