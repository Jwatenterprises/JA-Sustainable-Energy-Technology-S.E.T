# S.E.T. Sustainable Energy Technology in Jamaica WooCommerce Setup - shop.setjamaica.com

Status: setup track opened 2026-05-29. Hostinger WordPress site and Cloudflare DNS connected 2026-05-29.

Decision: build WooCommerce on `shop.setjamaica.com` so the live GitHub Pages authority site at `www.setjamaica.com` remains undisturbed.

## Architecture

| Layer | Decision |
| --- | --- |
| Main site | GitHub Pages: `https://setjamaica.com` and `https://www.setjamaica.com` |
| Store | WordPress + WooCommerce on `https://shop.setjamaica.com` |
| DNS | Cloudflare manages `shop` record once hosting target is known |
| Email | `info@setjamaica.com` via Google Workspace / Brevo for operational sending |
| Store model | Quote-first solar catalog plus low-ticket accessory checkout |
| Payments | Manual quote/invoice first; online card payments only after policies and supplier lanes are verified |

## Hosting Requirement

Use managed WordPress/WooCommerce hosting that supports:

- PHP 8.3 or newer.
- MySQL 8.0+ or MariaDB 10.6+.
- HTTPS/SSL.
- Apache or Nginx with rewrite support.
- Cron/background tasks for WooCommerce.
- Backups and staging.

Do not point `shop.setjamaica.com` until the host gives one of these:

- CNAME target, for example `shops.hostingprovider.com`.
- A record IP address.
- Nameserver instructions specifically for a subdomain.

## Store Identity

| Field | Value |
| --- | --- |
| Store name | S.E.T. Sustainable Energy Technology in Jamaica Shop |
| Legal/public brand | S.E.T. Sustainable Energy Technology in Jamaica / Sustainable Energy Technology |
| Store URL | `https://shop.setjamaica.com` |
| Main website | `https://www.setjamaica.com` |
| Store email | `info@setjamaica.com` |
| Phone/WhatsApp | `1-857-445-9407` |
| Country | Jamaica |
| Currency | JMD first; USD optional later |
| Launch geography | Jamaica only |

## Store Lanes

### Lane 1 - Quote Request Solar Packages

Use for:

- Rooftop solar assessments.
- 3 kW, 5 kW, and 10 kW hybrid solar packages.
- LiFePO4 battery backup.
- Church, school, and SME energy audits.
- Solar water heater bundles.

Rules:

- No direct checkout.
- No final price promises.
- Quote must say final cost depends on site visit, equipment availability, freight, customs/import handling, installer review, and written quotation.

### Lane 2 - Low-Ticket Checkout Products

Use for:

- Solar motion/security lights.
- Emergency solar lanterns.
- Solar power banks.
- Portable fans.
- Energy monitors.
- LED bulbs and small efficiency accessories.

Rules:

- Only publish checkout products after supplier confirms Jamaica delivery, warranty, return path, and replacement handling.
- Order samples before listing any safety-sensitive or high-failure item.

### Lane 3 - Lead Capture Products

Use for:

- Free solar readiness review.
- Hurricane backup consultation.
- Parish-specific energy review.

Rules:

- These are zero-price service intake items or forms, not normal products.
- Route submissions to `info@setjamaica.com`.

## Plugin Stack

Install minimum stack first:

| Need | Plugin / Tool |
| --- | --- |
| Store engine | WooCommerce |
| Quote workflow | Request a Quote for WooCommerce or YITH Request a Quote |
| Forms | Fluent Forms, WPForms, or Gravity Forms |
| SMTP | WP Mail SMTP or Brevo SMTP/API integration |
| SEO | Rank Math or Yoast SEO |
| Security | Wordfence or Solid Security |
| Backups | UpdraftPlus or host-level daily backups |
| Performance | LiteSpeed Cache if on LiteSpeed hosting; otherwise host-recommended cache |

Avoid Syncee/CJdropshipping automation until at least 5 starter products have passed supplier verification.

## Pages To Create

1. Home / Shop landing.
2. Solar Packages.
3. Solar Accessories.
4. Request a Quote.
5. Shipping & Delivery.
6. Returns & Refunds.
7. Warranty & Installation.
8. Privacy Policy.
9. Terms of Sale.
10. Contact.

## Starter Build Steps

1. Provision WordPress hosting for `shop.setjamaica.com`.
2. Create WordPress admin user with strong password and 2FA.
3. Install SSL.
4. Point Cloudflare `shop` DNS to the host target.
5. Install WooCommerce.
6. Configure Jamaica store identity, currency, taxes disabled/manual at first, and shipping zones as quote/manual.
7. Install request-quote plugin and forms plugin.
8. Import starter product CSV: `SET-JAMAICA-WOOCOMMERCE-STARTER-PRODUCTS.csv`.
9. Add policy pages from `SET-JAMAICA-WOOCOMMERCE-POLICIES.md`.
10. Test email delivery to `info@setjamaica.com`.
11. Test quote form, cart behavior, checkout disabled/limited behavior, and mobile.
12. Add `Shop Plan` link on the GitHub Pages site only after SSL and test order/quote flow pass.

## Launch Gate

Do not publicly launch until these pass:

- `https://shop.setjamaica.com` loads with valid HTTPS.
- Admin login has 2FA.
- Backup is active.
- Quote form sends to `info@setjamaica.com`.
- No high-ticket solar package can be purchased by accident.
- All public pages avoid hard customs, tax, incentive, financing, or approval guarantees.
- Footer links point back to `https://www.setjamaica.com`.
- Test mobile checkout/quote flow works.

## DNS Template

Add one of these in Cloudflare after hosting target is known:

```text
Type: CNAME
Name: shop
Target: [host-provided-cname]
Proxy: DNS only for initial SSL provisioning; proxy can be reviewed later
```

or:

```text
Type: A
Name: shop
IPv4 address: [host-provided-ip]
Proxy: DNS only for initial SSL provisioning; proxy can be reviewed later
```

## Open Blocker

Resolved 2026-05-29:

- Host: Hostinger Business.
- Website: `shop.setjamaica.com`.
- Hosting username: `u202238000`.
- Hosting order ID: `1009426716`.
- Web root: `/home/u202238000/domains/shop.setjamaica.com/public_html`.
- Cloudflare DNS records created:
  - `A shop -> 82.29.157.110`
  - `AAAA shop -> 2a02:4780:2b:2016:0:c0d:e830:2`
- HTTP verification: `http://shop.setjamaica.com` returns `200`.
- WordPress verification: `http://shop.setjamaica.com/wp-json/` returns `200`; `/wp-admin/` redirects to WordPress login.

Current blockers:

1. HTTPS is not active yet for `https://shop.setjamaica.com`; SSL must be enabled/provisioned in Hostinger hPanel or allowed time to auto-provision.
2. WooCommerce/plugin setup requires WordPress admin access, WordPress application password, SFTP/SSH, or an active browser session. Hostinger API can confirm hosting and DNS details but does not expose WordPress plugin installation for this shared hosting account.
