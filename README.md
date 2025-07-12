🛠️ Building the Executable (.exe or Linux ELF)
Prerequisites
You need to have the following installed:

Python 3.10+ (preferably)

keystone-engine

unicorn

pyinstaller

Optional: patchelf (for Linux portable builds)

Install them using:

bash
Always show details

Copy
pip install keystone-engine unicorn pyinstaller
sudo apt install patchelf  # Linux only
🔧 Step-by-Step: Build Executable
bash
Always show details

Copy
# Step 1: Find shared libraries
find $(python -c "import keystone; print(keystone.__file__)") -name "*.so"
find $(python -c "import unicorn; print(unicorn.__file__)") -name "*.so"

# Step 2: Use PyInstaller to bundle your script with the dynamic libraries:
pyinstaller --onefile funscript.py \
  --add-binary "/full/path/to/libkeystone.so:." \
  --add-binary "/full/path/to/libunicorn.so:."
Replace /full/path/to/... with the actual .so paths you found.

🔗 Optional: Make the Executable Portable
Set the runtime library path so the bundled .so files are found automatically:

bash
Always show details

Copy
patchelf --set-rpath '$ORIGIN' dist/funscript
Now you can run it like:

bash
Always show details

Copy
./dist/funscript test.funscript
Without needing LD_LIBRARY_PATH.

📂 Example
funscript
Always show details

Copy
```
def main() then
    print "Enter your name:"
    iread "Name: "
    let name := _
    print "Hello,"
    print name

    unsafe asm """
        mov eax, 2
        mov ebx, 3
        add eax, ebx
    """

    print "EAX calculation done."
    return
end
```
