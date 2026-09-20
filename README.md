We are building coding assisstance agent which can work with any LLM which is running local or in cloud.

### Local model setup
 You can ignore this step if you are using hosted llms.

- Get gemm4 model suitable for your system configurations from here https://gemmai4.com/download/#picker

```bash
# macOS / Linux (Sort blobs by size to find the largest file)
ls -lh ~/.ollama/models/blobs/
```
```
# Replace <LARGE_BLOB_HASH> with the hash of the multi-GB file
cp ~/.ollama/models/blobs/sha256-<LARGE_BLOB_HASH> ./models/gemma4-e4b-it-qat.gguf
```

- Install llama server
```bash
brew install llama.cpp
```
- Verify the installation
```bash
llama-server --help
```
- Run LLM
```bash
llama-server -m ./models/gemma4-e4b-it-qat.gguf --port 8080 -c 4096 -ngl 99
```


## Steps

- Install uv (package manager) from https://docs.astral.sh/uv/getting-started/installation/

- Run following commands

``` bash 
uv sync # to install the dependencies
```
``` bash
source .venv/bin/activate # activate virtual env
```
- Create OpenAI API key [here](https://platform.openai.com/api-keys)

- Update env 
```bash
# Create .env file
cp .env.example .env
# update OPENAI_API_KEY with above created API key in env
OPENAI_API_KEY='your_openai_api_key_here'
```
- Open langsmith studio
```bash
uv run langgraph dev
```