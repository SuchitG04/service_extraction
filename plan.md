- from package.json, extract all the dependencies and identify all the potential external data-sending libraries (using an LLM)
- grep the files (flagged as data sinks by qwen). send only these files to the LLM to extract the external services
- Note: use both package.json s available in the twenty repo since they seem to have some mutually exclusive dependencies

- I have the libraries identified to potentially have external services
- I also have the files in which these libraries are being imported


- you have an import graph. 
say you have 2 files A and B
B imports foo from A
the directed graph would have an edge B -> A

- you have a bunch of files flagged as having sinks. just see if these files have a directed edge to any of the files found by the grep thingy 

- these (previously) flagged files would have the service names. find those service names in the AST. check if these service names appear in the files found by the grep thingy

- check the service names definition/initialization too. maybe you can trace it back?? when traced, if it is connected to the imports from potential externally communicating libraries, then you have your external service

