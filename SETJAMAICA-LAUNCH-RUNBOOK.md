# S.E.T. Jamaica Launch Runbook

## Domain
- Primary domain: setjamaica.com
- GitHub Pages CNAME file: setjamaica.com
- Defensive domain: www-set-jamaica.com

## Cloudflare DNS for GitHub Pages
Add these records in the `setjamaica.com` Cloudflare zone:

| Type | Name | Content | Proxy |
| --- | --- | --- | --- |
| A | @ | 185.199.108.153 | DNS only |
| A | @ | 185.199.109.153 | DNS only |
| A | @ | 185.199.110.153 | DNS only |
| A | @ | 185.199.111.153 | DNS only |
| AAAA | @ | 2606:50c0:8000::153 | DNS only |
| AAAA | @ | 2606:50c0:8001::153 | DNS only |
| AAAA | @ | 2606:50c0:8002::153 | DNS only |
| AAAA | @ | 2606:50c0:8003::153 | DNS only |
| CNAME | www | jwatenterprises.github.io | DNS only |

Then in GitHub repo settings:
- Pages source: `main` branch, root folder
- Custom domain: `setjamaica.com`
- Enforce HTTPS: enabled after certificate is issued

## Google Workspace Email
Primary user:
- info@setjamaica.com

Free aliases to add after Gmail is live:
- wayne@setjamaica.com
- sales@setjamaica.com
- hello@setjamaica.com
- contact@setjamaica.com

After MX records are active:
1. Add aliases in Google Admin.
2. Configure "Send mail as" in Gmail for public aliases.
3. Generate DKIM in Google Admin and add the CNAME in Cloudflare.
4. Add DMARC TXT:

```text
v=DMARC1; p=none; rua=mailto:postmaster@setjamaica.com
```

Cloudflare MX record:

| Type | Name | Mail server | Priority | Proxy |
| --- | --- | --- | --- | --- |
| MX | @ | smtp.google.com | 1 | DNS only |

Remove any other MX records before activating Gmail.

## Site Wiring
- Lead form currently opens a prefilled email to info@setjamaica.com.
- Newsletter is still a local confirmation stub; wire to Mailchimp, Beehiiv, Substack, or Formspree before paid traffic.
- Footer social links are placeholders until real S.E.T. Jamaica profiles exist.
- Footer FAQ / Maintenance / Warranty / Privacy links point to planned sections or pages.

## Redirect
Set `www-set-jamaica.com` to 301 redirect to:

```text
https://setjamaica.com
```
