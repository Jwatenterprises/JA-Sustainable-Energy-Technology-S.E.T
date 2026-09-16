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
v=DMARC1; p=none; rua=mailto:info+dmarc@setjamaica.com
```

2026-06-06 update: DMARC aggregate reports were moved away from the plain `info@setjamaica.com` reporting address to the report-specific Google Workspace plus address `info+dmarc@setjamaica.com`. Next cleanup option: create a Gmail filter for mail delivered to `info+dmarc@setjamaica.com` or replace this with a true dedicated `dmarc@setjamaica.com` mailbox/parser address after it is provisioned.

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

## WooCommerce Store - shop.setjamaica.com

Decision confirmed 2026-05-29:
- Keep the main site on GitHub Pages.
- Build WordPress + WooCommerce separately on `shop.setjamaica.com`.
- Use quote-first solar packages plus low-ticket accessory checkout only after supplier verification.

Prepared files:
- `SET-JAMAICA-WOOCOMMERCE-SETUP.md`
- `SET-JAMAICA-WOOCOMMERCE-STARTER-PRODUCTS.csv`
- `SET-JAMAICA-WOOCOMMERCE-POLICIES.md`

DNS completed 2026-05-29:

```text
Type: A
Name: shop
Target: 82.29.157.110
Proxy: DNS only
```

```text
Type: AAAA
Name: shop
Target: 2a02:4780:2b:2016:0:c0d:e830:2
Proxy: DNS only
```

Hostinger website:

```text
Domain: shop.setjamaica.com
Hosting plan: Hostinger Business
Hosting username: u202238000
Order ID: 1009426716
Root: /home/u202238000/domains/shop.setjamaica.com/public_html
```

Verified:
- `http://shop.setjamaica.com` returns `200`.
- `http://shop.setjamaica.com/wp-json/` returns `200`.
- `/wp-admin/` is reachable and redirects to WordPress login.

Pending:
- Enable/provision SSL for `https://shop.setjamaica.com`.
- Log in to WordPress and install WooCommerce + setup plugins.

When the WordPress/WooCommerce host provides DNS instructions, add one of:

```text
Type: CNAME
Name: shop
Target: [host-provided-cname]
Proxy: DNS only for first SSL provisioning
```

or:

```text
Type: A
Name: shop
IPv4 address: [host-provided-ip]
Proxy: DNS only for first SSL provisioning
```
