#Assignment 2

## Author
* **Ioannis Manolas**

---

## Assignment Specification

Using the patent claims collection in XML format, write a Python algorithm to process the claims. The algorithm should take as input all claims retrieved via BeautifulSoup (`claims = soup.find_all('claims')`) and perform the following:

1. **TREC Format Output:** Write an output file containing the patent document ID (`<DOCNO>`) and each individual claim enclosed in corresponding numbered tags (e.g., `<CLAIM1>`, `<CLAIM2>`).
2. **Classification & Union:** Write three additional tags:
   * `<INDEPEDENT>`: Lists independent claims (claims that do not rely on another claim).
   * `<DEPEDENT>`: Lists dependent claims (claims that rely on another claim).
   * `<UNION>`: Merges and links dependent claims with their corresponding base claims.

---

## Solution Overview

For the solution of the 2nd part, we used the Python programming language to create a script that iterates through all existing patent files to process and clean them, properly separating the claims tags.

### Key Processing Steps:
* **Claim Segmentation:** Automatically handles multiple structural variants in the XML documents (e.g., numbered tags, single claim-text blocks, or unstructured formats).
* **Classification:** Groups claims into dependent and independent categories.
* **Union Mapping:** Links dependent claims back to their base claims using a multi-language keyword dictionary (supporting English, German, and French terms such as *claim*, *Anspruch*, and *revendication*).

### Python Libraries Used:
* **`numpy`**: For data storage.
* **`pandas`**: For data storage and processing.
* **`os`**: For opening and writing to external files.
* **`re`**: For finding and processing data using regular expressions.
* **`BeautifulSoup` & `lxml`**: For extracting data from `.xml` format files with specific tags.

The final script was executed across all data (106,087 patent document files), writing the structured results into an output file partitioned by document ID (`<DOCNO>`).

---

## Output Format Example

```xml
<DOCNO>
EP-0003401-A1
</DOCNO>
<CLAIMS>
<CLAIM1>
1. A cutter assembly comprising a housing, a member slidable within the housing...
</CLAIM1>
<CLAIM2>
2. A cutter assembly as in claim 1 wherein the housing has a cavity therein...
</CLAIM2>
</CLAIMS>
<INDEPEDENT>
[1]
</INDEPEDENT>
<DEPEDENT>
[2]
</DEPEDENT>
<UNION> 
UNION CLAIM 1 :
1. A cutter assembly comprising a housing..., wherein the housing has a cavity therein...
</UNION>
