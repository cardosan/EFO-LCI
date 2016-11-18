# LCIFE: Life Cycle Inventory of European forest management

## About

The Life Cycle Inventory of European forest management Biomass And Allometry Database (LCIFE) contains life cycle inventory (LCI) data on the forest management practices of 29 countries within the European subcontinent based on a questionnaire filled by silvicultural experts.We first classified European forest on the basis of what we called "forest unit" (the combination of silvicultural practices and tree species) and, for each Forest Unit (FU) we constructed a LCI.

These data were gathered from over 170 published and unpublished scientific studies, most of which was not previously available in the public domain. It is our hope that making these data available will improve our ability to understand plant growth, ecosystem dynamics, and carbon cycling in the world's woody vegetation. The dataset is described further in the publication

ADD CITATION

At time of publication, the LCIFE contained 29 countries and 235 FUs described in 29 different European countries .

Details about individual studies contributed to the BAAD are given are available in these [online reports](https://github.com/dfalster/baad/wiki).

## Using BAAD

The data in LCIFE are released under the [Creative Commons Zero](https://creativecommons.org/publicdomain/zero/1.0/) public domain waiver, and can therefore be reused without restriction. To recognise the work that has gone into building the database, we kindly ask that you cite the above article, or when using data from only one or few of the individual studies, the original articles if you prefer.

There are two options for accessing data within BAAD.

### Download compiled database

You can download a compiled version of the database from either:

1. Ecological Archives. This is the version of the database associated with the corresponding paper in the journal [*Ecology*]. [Link](http://www.esapubs.org/archive/ecol/E096/128/).
2. Releases we have posted on [github](https://github.com/dfalster/baad/releases).
3. The [baad.data](https://github.com/traitecoevo/baad.data) package for `R`.

The database contains the following elements

- `data`: amalgamated dataset (table), with columns as defined in `dictionary`
- `dictionary`: a table of variable definitions
- `metadata`: a table with columns "studyName","Topic","Description", containing written information about the methods used to collect the data
- `methods`: a table with columns as in data, but containing a code for the methods used to collect the data. See [config/methodsDefinitions.csv](config/methodsDefinitions.csv) for codes.
- `references`: as both summary table and bibtex entries containing the primary source for each study
- `contacts`: table with contact information and affiliations for each study
These elements are available at both of the above links as a series of CSV and text files.

If you are using `R`, by far the best way to access data is via our package [baad.data](https://github.com/traitecoevo/baad.data).  After installing the package (instructions [here](https://github.com/traitecoevo/baad.data)), users can run

```r
baad.data::baad_data("1.0.0")
```

to download the version stored Ecological Archives, or

```r
baad.data::baad_data("x.y.z")
```

to download an earlier or more recent version (where version numbers will follow the [semantic versioning](http://semver.org) guidelines. The baad.data package caches everything so subsequent calls, even across sessions, are very fast.  This should facilitate greater reproducibility by making it easy to depend on the version used for a particular analysis, and allowing different analyses to use different versions of the database. 

Further details about the different versions and changes between versions is available on the [github releases](https://github.com/dfalster/baad/releases) page and in the [CHANGELOG](CHANGELOG.md).

## Details about the data distribution system

The BAAD is designed to be a living database -- we will be making periodic releases as we add more data. These updates will correspond with changes to the version number of this resource, and each version of the database will be available on [github](https://github.com/dfalster/baad/releases) and via the [baad.data](https://github.com/traitecoevo/baad.data) package. If you use this resource for a published analysis, please note the version number in your publication.  This will allow anyone in the future to go back and find **exactly** the same version of the data that you used.

### Rebuilding from source

The BAAD can be rebuilt from source (raw data files) using our scripted workflow in R. Beyond base R, building of the BAAD requires the package ['remake'](https://github.com/richfitz/remake). To install remake, from within R, run:

```
# installs the package devtools
install.packages("devtools")
# use devtools to install remake
devtools::install_github("richfitz/remake")
```

A number of other packages are also required (`rmarkdown, knitr, knitcitations, plyr, whisker, maps, mapdata, gdata, bibtex, taxize, Taxonstand, jsonlite`). These can be installed either within R using `install.packages`, or more easily using remake (instructions below).

The database can then be rebuilt using remake.

First download the code and raw data, either from Ecological Archives or from github as either [zip file](https://github.com/dfalster/baad/archive/master.zip), or by cloning the baad repository:

```
git clone git@github.com:dfalster/baad.git
```

Then open R and set the downloaded folder as your working directory. Then,

```
# ask remake to install any missing packages
remake::install_missing_packages()

# build the dataset
remake::make("export")

# load dataset into R
baad <- readRDS('export/baad.rds')
````

A copy of the dataset has been saved in the folder `export` as both `rds` (compressed data for R) and also as csv files.

## Reproducing older versions of the BAAD and the paper from Ecology

You can reproduce any version of the BAAD by checking out the appropriate commit that generated, or using the links provided under the [releases tab](https://github.com/dfalster/baad/releases). For example, to reproduce v1.0.0 of the database, corresponding to the paper in Ecology and the manuscript submitted to Ecology:

```
git checkout v1.0.0
```

Then in R run
```
remake::make("export")
remake::make("manuscript")
```

## Contributing data to the BAAD

We welcome further contributions to the BAAD.

If you would like to contribute data, the requirements are

1. Data collected are for woody plants
2. You collected biomass or size data for multiple individuals within a species
3. You collected either total leaf area or at least one biomass measure
4. Your biomass measurements (where present) were from direct harvests, not estimated via allometric equations.
5. You are willing to release the data under the [Creative Commons Zero](https://creativecommons.org/publicdomain/zero/1.0/) public domain dedication.

See [these instructions](CONTRIBUTING.md) on how to prepare and submit your contribution.

Once sufficient additional data has been contributed, we plan to submit an update to the first data paper, inviting as co authors anyone who has contributed since the first data paper.

## Acknowledgements

We are extremely grateful to everyone who has contributed data. We would also like to acknowledge the following funding sources for supporting the data compilation. D.S. Falster, A. Vårhammer and D.R. Barneche were employed on an ARC discovery grant to Falster (DP110102086) and a UWS start-up grant to R.A. Duursma. R.G. FitzJohn was supported by the Science and Industry Endowment Fund (RP04-174). M.I. Ishihara was supported by the Environmental Research and Technology Development Fund (S-9-3) of the Ministry of the Environment, Japan.

![baad logo](https://github.com/dfalster/baad/raw/master/extra/baad.png)

