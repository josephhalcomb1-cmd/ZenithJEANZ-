# Putting zenithjeanz.com live

The plan:

| Address | Serves | Hosted by |
|---|---|---|
| `zenithjeanz.com` (and `www.`) | The runway site (`index.html` + `media/`) | GitHub Pages (free; this repo is public) |
| `shop.zenithjeanz.com` | Checkout, order emails and customer accounts | Shopify |

Do these in order. DNS changes can take anywhere from a few minutes to a few hours to
take effect.

## 1. Turn on GitHub Pages (2 min)

1. Open https://github.com/josephhalcomb1-cmd/ZenithJEANZ-/settings/pages
2. Under **Build and deployment**:
   - **Source:** Deploy from a branch
   - **Branch:** `master`, folder `/ (root)`
   - Press **Save**.
3. After about a minute, the page shows a link like
   `https://josephhalcomb1-cmd.github.io/ZenithJEANZ-/`. Open it and check that the
   runway plays.

Don't fill in the **Custom domain** box yet. That comes in step 3, after DNS is set.

## 2. Add the DNS records in Squarespace (10 min)

1. Sign in at https://account.squarespace.com/domains and open **zenithjeanz.com**.
2. Go to **DNS** (sometimes called **DNS Settings**).
3. If there's a **Squarespace Defaults** record group, delete it. Its records would
   point the domain at a Squarespace site and conflict with the ones below.
4. Under **Custom records**, add each row below. Leave TTL at the default.

**For the runway site (GitHub Pages)**

| Host | Type | Data |
|---|---|---|
| `@` | A | `185.199.108.153` |
| `@` | A | `185.199.109.153` |
| `@` | A | `185.199.110.153` |
| `@` | A | `185.199.111.153` |
| `@` | AAAA | `2606:50c0:8000::153` |
| `@` | AAAA | `2606:50c0:8001::153` |
| `@` | AAAA | `2606:50c0:8002::153` |
| `@` | AAAA | `2606:50c0:8003::153` |
| `www` | CNAME | `josephhalcomb1-cmd.github.io` |

**For Shopify**

| Host | Type | Data |
|---|---|---|
| `shop` | CNAME | `shops.myshopify.com` |

Leave any **MX** records alone if you have email on this domain.

## 3. Connect the domain in GitHub (2 min)

1. Back on the Pages settings page, type `zenithjeanz.com` in **Custom domain** and
   press **Save**. GitHub runs a DNS check, then adds a `CNAME` file to the repo.
2. When the check passes, tick **Enforce HTTPS**. The tick box may stay greyed out for
   up to an hour while GitHub issues the certificate.

## 4. Connect the subdomain in Shopify (3 min)

1. In Shopify admin, open **Settings → Domains → Connect existing domain**.
2. Enter `shop.zenithjeanz.com` and press **Next**, then **Verify connection**.
3. Set `shop.zenithjeanz.com` as the **primary domain**. Checkout, order emails and
   the `/account` login then all use it.

Don't connect the bare `zenithjeanz.com` in Shopify. That address belongs to the
runway site.

## 5. Final check

- `https://zenithjeanz.com` → the runway site, with the padlock showing.
- `https://www.zenithjeanz.com` → redirects to the runway site.
- `https://shop.zenithjeanz.com` → your Shopify store.
- On the runway, add something to the cart and press **Checkout**. It should open
  Shopify's checkout on `shop.zenithjeanz.com`. This works once the store is
  connected, see `SHOPIFY_SETUP.md`.

## Good to know

- **The Shopify online store theme still exists** at `shop.zenithjeanz.com`. Shoppers
  normally never land there, but you can make its homepage point back to
  `zenithjeanz.com` later (Online Store → Navigation, or a one-line theme redirect).
- **Trial stores can't take real payments.** Checkout won't accept payment until you
  pick a paid plan and set up payments. Use test mode to try it before then.
- **Updating the site later:** run `python3 build.py`, commit and push to `master`.
  GitHub Pages republishes within a minute or two.
