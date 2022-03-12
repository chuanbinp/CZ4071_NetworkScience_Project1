# CZ4071_NetworkScience_Project1

---

## 0. data_collection.ipynb

### Extract Data

Read in excel file from _Input/DataScientist.xls_  
For each http address in the dblp column:

1. Get the PID from the redirected address
2. Skip if seen this PID before (prevent duplicates), else update seen list (pid_list) and name mapping (pid_name_mapping)
3. Use bs4 to extract xml
4. Skip if this PID is non-existent (prevent error if no such records)
5. Get all articles and extract ['author_pid','coauthor_pid','year','title']
6. Add to dataframe network_df

Save raw data under _Input/RawNetworkDataFrame.csv_

### Process raw data

-   Remove individuals not in the network using seen list (pid_list)
-   Add author_name and coauthor_name columns using name mapping (pid_name_mapping)
-   Remove duplicates since edges are bidirectional, remove if row data is same when author and coauthor is swapped
    -   Create a check_duplicates string for each row in the format `<sorted[author_pid,coauthor_pid]><title><year>.`
    -   Rationale of doing sorted is to ensure directional relationships are ignored to prevent duplicates (A->B and B->A are treated the same)

Save processed data under _Input/ProcessedNetworkDataFrame.csv_

## 1. Webapp

### Run

1. cd into ./Input folder
2. Open terminal and run `pip install -r requirements.txt`
3. Run `py project.py`
4. Go to <http://127.0.0.1:8050/>

### Features

-   Year slider to visualise how network evolved over time
-   Tab between the actual network and a random network generated using the Erdos-Renyi Model, G(n,p) where p = 0.03
-   Log-log degree distribution and network properties table update with input
-   Note: due to large data, loading time is long, esp when viewing random network
    -   Degree distribution and properties table update faster
-   Demo video here: <https://youtu.be/U0BgUR8zhtM/>
