# awanninger.com auth.md

How AI agents and other automated clients access awanninger.com.

## Audience

AI agents, crawlers and other automated clients that read awanninger.com, the
personal landing page of Adam Wanninger.

## Registration and provisioning

None. This is a static site with no accounts, no API and no login. There is no
registration endpoint and nothing to provision: no `/agent/auth`, no OAuth
authorization server and no OAuth protected resource metadata. Don't look for
them, and don't try to register.

## Supported methods

Anonymous, unauthenticated HTTPS `GET` requests. Everything is public:

- `https://awanninger.com/`: the page (HTML). Send `Accept: text/markdown`
  to get the Markdown version instead.
- `https://awanninger.com/index.md`: the page as Markdown
- `https://awanninger.com/llms.txt`: concise overview for LLMs
- `https://awanninger.com/llms-full.txt`: full detail for LLMs
- `https://awanninger.com/robots.txt`: crawl and usage policy
- `https://awanninger.com/sitemap.xml`: sitemap
- `https://awanninger.com/.well-known/api-catalog`: API catalog (empty, since
  there are no APIs)

## Credential use

None. No credentials are issued or accepted. Don't send cookies, bearer tokens
or API keys.

## Usage policy

`robots.txt` allows all crawlers (`Allow: /`) and declares
`Content-Signal: search=yes, ai-input=yes, ai-train=yes`.

## Contact

Adam would love to hear from agents. Say hello at adam@awanninger.com.
