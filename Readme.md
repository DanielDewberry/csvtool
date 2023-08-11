# CSV Tool

Reshape a CSV file.

## Installation

```bash
chown "${USER}:${USER}" csvtool.py
chmod 755 csvtool.py
cp csvtool.py ~/.local/bin/csvtool
```


## Usage

Selections and Projections indexes are zero-based.



### Print a projection of column numbers

```bash
./csvtool 0 1 2 < ~/Downloads/mm23.csv
```


### Read from file

csvtool reads from stdin by default, but can be instructed to open a file for reading

```bash
./csvtool --input ~/Downloads/mm23.csv 0 1 2
```


### Write to file

csvtool writes to stdout by default, but can be instructed to open a file for writing:

```bash
./csvtool \
    --input ~/Downloads/mm23.csv \
    --output ~/Downloads/mm23-processed.csv \
    0 1 2
```


### Address columns by header names

Instruct csvtool to use column names from the first post-filter row

```bash
./csvtool \
    --input ~/Downloads/mm23.csv \
    --output ~/Downloads/mm23-processed.csv \
    --named \
    'Title' 'CPI INDEX 00: ALL ITEMS 2015=100'
```


### Rename the output columns

```bash
./csvtool \
    --input ~/Downloads/mm23.csv \
    --output ~/Downloads/mm23-processed.csv \
    --named \
    'Title' 'CPI INDEX 00: ALL ITEMS 2015=100' \
    --new 'Title' 'CPI INDEX'
```


### Suppress headers

```bash
./csvtool \
    --input ~/Downloads/mm23.csv \
    --output ~/Downloads/mm23-processed.csv \
    --named \
    'Title' 'CPI INDEX 00: ALL ITEMS 2015=100' \
    --no-print-header
```


### Filter records

```bash
./csvtool \
    --input ~/Downloads/mm23.csv \
    --output ~/Downloads/mm23-processed.csv \
    --named \
    'Title' 'CPI INDEX 00: ALL ITEMS 2015=100' \
    --new 'title' 'cpi index' \
    --filter '0,14-'
```


### Invert the record filter

```bash
./csvtool \
    --input ~/Downloads/mm23.csv \
    --output ~/Downloads/mm23-processed.csv \
    --named \
    'Title' 'CPI INDEX 00: ALL ITEMS 2015=100' \
    --new 'Title' 'CPI INDEX' \
    --filter '1-13' --invert-filter
```


## Examples

### Reduce and print the mm23.csv UK CPI data

Example [data source](https://www.ons.gov.uk/file?uri=%2Feconomy%2Finflationandpriceindices%2Fdatasets%2Fconsumerpriceindices%2Fcurrent%2Fmm23.csv) [from](https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/consumerpriceindices).


```bash
./csvtool \
    --input ~/Downloads/mm23.csv \
    --named \
    'Title' \
    'CPI INDEX 00: ALL ITEMS 2015=100' \
    'CPI ANNUAL RATE 00: ALL ITEMS 2015=100' \
    'CPI MONTHLY RATE 00: ALL ITEMS 2015=100' \
    'CPIH INDEX 00: ALL ITEMS 2015=100' \
    'CPIH ANNUAL RATE 00: ALL ITEMS 2015=100' \
    'CPIH MONTHLY RATE 00: ALL ITEMS 2015=100' \
    'RPI All Items Index: Jan 1987=100' \
    --new \
    'Title' \
    'CPI INDEX' \
    'CPI ANNUAL RATE' \
    'CPI MONTHLY RATE' \
    'CPIH INDEX' \
    'CPIH ANNUAL RATE' \
    'CPIH MONTHLY RATE' \
    'RPI All Items Index' \
    --filter '1-13' --invert-filter
```

### csvtool | psql

```sql
create unlogged table loadtable8c(
    aa text,
    ab text,
    ac text,
    ad text,
    ae text,
    ef text,
    eg text,
    eh text
);
```

```bash
./csvtool \
    --input ~/Downloads/mm23.csv \
    --named \
    'Title' \
    'CPI INDEX 00: ALL ITEMS 2015=100' \
    'CPI ANNUAL RATE 00: ALL ITEMS 2015=100' \
    'CPI MONTHLY RATE 00: ALL ITEMS 2015=100' \
    'CPIH INDEX 00: ALL ITEMS 2015=100' \
    'CPIH ANNUAL RATE 00: ALL ITEMS 2015=100' \
    'CPIH MONTHLY RATE 00: ALL ITEMS 2015=100' \
    'RPI All Items Index: Jan 1987=100' \
    --filter '1-13' --invert-filter |
    psql -c "\copy loadtable8c from STDIN with (format 'csv', quote '\"', encoding 'utf8');"
```
