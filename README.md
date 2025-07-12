# FunScript

FunScript is a simple scripting language interpreter written in Python that supports:

- Defining and calling functions  
- `print` statements  
- `iread` for user input  
- Inline x86 assembly execution using Keystone and Unicorn  
- Basic error handling  

---

## Requirements

- Python 3.8 or higher  
- [Keystone engine](https://www.keystone-engine.org/)  
- [Unicorn engine](https://www.unicorn-engine.org/)  
- Python packages: `keystone-engine`, `unicorn`  

Install the required Python packages with:

```bash
pip install keystone-engine unicorn
