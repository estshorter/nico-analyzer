# AI Agent Guidance

## Environment Management

### Python Environment
When executing Python scripts or managing dependencies, you **must** use `uv`.

- **Reason**: `uv` provides faster and more reliable environment management.
- **Commands**:
  - Run a script: `uv run <script_path>`
  - Install dependencies: `uv pip install <package_name>`
  - Add to requirements: `uv add <package_name>`

## Data Preprocessing Rules

### Software Talk Data Filtering
When analyzing data from `results/software_talk.pickle`, you **must** apply the `filter_software_talk` function from `common_utils.py`.

- **Reason**: The `software_talk` category often contains singing-related videos (VOCALOID, music, etc.) that can skew analysis results if not removed.
- **Implementation**:
  ```python
  from common_utils import filter_software_talk
  
  # After loading the DataFrame from software_talk.pickle
  df = filter_software_talk(df)
  ```
- **Filter Criteria**: Currently excludes tags matching `VOCALOID|VOCAROID|音楽|歌うボイスロイド|CeVIOカバー曲|歌ってみた`.
