---
title: "Code Blocks"
slug: "code-blocks"
---
## Displaying Code

! Inserting code snippets is simple. Code blocks are written in a proportional font and are equipped with syntax highlighting (using the `highlight` plugin) for improved readability.

### File Header (Code Header Plugin)
You can add a header to code blocks, for example, for the file name that the code block belongs to. The syntax can be written in two ways, abbreviated using the parser:
€€€/etc/ansible/ansible.cfg
[defaults]
ansible_managed = Ansible managed: {file} modified by {uid} on {host}
€€€

The same, but written in HTML:

<div class="codeblock"><div class="codehead">/etc/ansible/ansible.cfg</div>
<pre><code>[defaults]
ansible_managed = Ansible managed: {file} modified by {uid} on {host}
</code></pre>
</div>

### Code Block Without a Header
#### YAML
```yaml
- name: Example from Ansible
  debug:
    var: ansible_facts.packages
```

#### Python
```python
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
```


---
**[Back to the absolute start of the demo](/doku)**