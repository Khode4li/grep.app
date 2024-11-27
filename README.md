# grep.app
I recently had an idea about creating wordlists by leveraging existing content on GitHub. While the data is readily available, I initially hesitated to develop the necessary tools. However, I discovered [grep.app](http://grep.app), a powerful application that enables unlimited GitHub repository searches without rate limits. This makes the process significantly more efficient and accessible.

This tool works by finding common patterns that programmers use to handle user inputs. For example, in Laravel, developers use `$request->validate` to validate user input. By searching for this pattern, we can use grep to extract parameter names from it.

To get started with the tool, run the following command:

```bash
git clone https://github.com/Khode4li/grep.app.git && cd grep.app && pip install typer && pip install bs4 && mv app.py /usr/local/bin/grepWL && chmod +x /usr/local/bin/grepWL
```

Usage Example:

```bash
grepWL '$request->validate' --s2f # this command saves all the source code containing $request->validate to output folder.
grep -h -oP "'\K[a-zA-Z0-9_]+(?=' *:)" output/* # extracts all parameter names from the files
rm -rf output # delete files
```
