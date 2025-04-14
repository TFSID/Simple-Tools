import pandas as pd
import sys

chunks = []


csvfile = pd.read_csv('acunetix.biofarma.csv', chunksize=100000, encoding="utf-8")

    
for chunk in pd.read_csv('acunetix.biofarma.csv', chunksize=100000, encoding="utf-8"):
    
    # Dropping multiple columns by name
    # print(chunk)
    
    chunk = chunk.drop(['Raw text Details', 'Parameter', 'AOP_SourceFile', 'AOP_SourceLine', 'AOP_Additional', 'IsFalsePositive', 'Impact', 'Description', 'Detailed Information', 'Recommendation', 'Request', 'CWEList', 'CVSS Descriptor', 'CVSS AV', 'CVSS AC', 'CVSS Au', 'CVSS C', 'CVSS I', 'CVSS A', 'CVSS E', 'CVSS RL', 'CVSS RC', 'CVSS3 Descriptor', 'CVSS3 Score', 'CVSS3 EnvScore', 'CVSS3 AV', 'CVSS3 AC', 'CVSS3 PR', 'CVSS3 UI', 'CVSS3 S', 'CVSS3 C', 'CVSS3 I', 'CVSS3 A', 'CVSS3 E', 'CVSS3 RL', 'CVSS3 RC', 'CVSS4 Descriptor', 'CVSS4 Score', 'CVSS4 AV', 'CVSS4 AC', 'CVSS4 AR', 'CVSS4 PR', 'CVSS4 UI', 'CVSS4 VC', 'CVSS4 VI', 'CVSS4 VA', 'CVSS4 SC', 'CVSS4 SI', 'CVSS4 SA', 'Reference (Name|Url)'], axis=1)
    
    # Dropping multiple columns by index
    # pd.drop([[0, 1]], axis=1, inplace=True)
    # print(chunk)
    
    
    chunks.append(chunk)
    
# print(chunks)
# sys.exit()
# Concatenate all processed chunks
df_modified = pd.concat(chunks)

# Write the concatenated DataFrame to a new CSV file
df_modified.to_csv('acunetix.biofarma.modified.csv', index=False)