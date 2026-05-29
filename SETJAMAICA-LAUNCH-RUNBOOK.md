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
1. [ ] Add aliases in Google Admin.
2. [ ] Configure "Send mail as" in Gmail for public aliases.
3. [x] Generate DKIM in Google Admin and add the CNAME in Cloudflare.
4. [x] Add DMARC TXT:

```text
v=DMARC1; p=none; rua=mailto:info@setjamaica.com
```

Cloudflare MX record:

| Type | Name | Mail server | Priority | Proxy |
| --- | --- | --- | --- | --- |
| MX | @ | smtp.google.com | 1 | DNS only |

Remove any other MX records before activating Gmail.

## Secure Sending (Maya/Cassidy)
- **Primary Provider:** Brevo (API Key in `.env`)
- **Config:** `email_config.json` set to `auth_type: brevo`.
- **Sender:** info@setjamaica.com (Verified in Brevo)

To test:
```bash
py C:\Users\Milli\.kiyomimax\send_email.py --test
```
## Redirect
Set `www-set-jamaica.com` to 301 redirect to:

```text
https://setjamaica.com
```
