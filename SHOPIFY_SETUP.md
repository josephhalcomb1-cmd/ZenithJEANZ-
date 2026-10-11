# Connecting the runway site to Shopify

Until these steps are done, the site runs in **demo mode**. Sizes, cart, wishlist,
search and filters all work. Checkout and Account show a message saying the store
isn't connected yet.

Once it's connected, checkout opens Shopify's secure checkout. Shopify handles card
payments, shipping, tax, order emails and customer accounts. The runway site stays
exactly as it looks now.

## 1. Create the store

Sign up at shopify.com. On the plan page, check that the plan includes the
**Headless** sales channel (step 3).

- Basic and higher include it.
- The cheapest Starter plan may not.

## 2. Import the products

1. In Shopify admin, go to **Products → Import**.
2. Upload `brand/shopify-products.csv` from this repo.
3. Tick **Publish new products to all sales channels**.

This creates all 23 pieces. Each piece gets sizes S–XXL at its price from the garment
sheet, and tags (`men`, `women`, `denim`, `look-01`…) for your own organisation.

**Don't change the product handles** (`zj-01-canvas-vest` and so on). The site uses them to
find each piece.

After the import:

- **Photos:** add product photos to each piece. They show on Shopify's checkout and
  order emails.
- **Stock:** inventory is untracked, so everything can always be bought. To limit
  stock, open a product, tick **Track quantity** and enter quantities. Sold-out sizes
  then appear crossed out on the site automatically.
- **Prices:** prices you change in Shopify override the ones on the site, so Shopify
  is the one place to edit them.

## 3. Get the Storefront API token

1. In Shopify admin, open the **Shopify App Store** and install **Headless**
   (published by Shopify).
2. Open **Sales channels → Headless → Create storefront**.
3. Under **Storefront API**, copy the **Public access token**.
4. Under **Manage permissions**, make sure product listings and checkouts (cart) are
   readable and writable.

The public token is designed to sit in website code. It can only read products and
create carts, never see orders or customer data. Never use the **private** token here.

Check that every product is published to the **Headless** channel. Open a product and
look under **Publishing** or **Sales channels**.

## 4. Plug it in

Edit `brand/store.json`:

```json
{
  "shopDomain": "your-store.myshopify.com",
  "storefrontToken": "paste-the-public-access-token",
  "apiVersion": "2025-07",
  "showsUrl": ""
}
```

- Use the `.myshopify.com` address, even if you also have a custom domain.
- `showsUrl` is optional. It makes the **Shows** nav link open a page, such as a show
  video or YouTube link. Left blank, Shows just returns to the full runway.

Then rebuild:

```sh
python3 build.py      # prints "Shopify connected"
```

## 5. Test

Serve the site, add a look and a single piece in different sizes, open the cart, and
press **Checkout**. You should land on Shopify's checkout with those items.

Use Shopify's test mode (**Settings → Payments → Bogus Gateway** or
**Shopify Payments test mode**) for a dummy order before going live.

If something doesn't appear, open the browser console:

- The site logs any handles it couldn't find in Shopify.
- The usual cause is a product not being published to the Headless channel.

## What each control does

| Control | Behaviour |
|---|---|
| Size picker | Chooses the size to buy. Sizes sold out in Shopify are crossed out. |
| Add to cart (right panel) | Adds every piece of the look in the chosen size. |
| More details → Add piece | Adds just that piece. |
| Cart icon | Opens the cart. Change quantities or remove items, then Checkout. |
| Checkout | Creates a Shopify cart and redirects to Shopify's checkout. |
| Heart icon | Shows only wishlisted looks. Tap again for all looks. |
| Add to wishlist | Saves the look on this device. |
| Search icon | Filters the runway by look or piece name, such as "bomber" or "jeans". |
| New arrivals / Women / Men / Denim | Filter the runway. Tap the active one again to show all. |
| Shows | Opens `showsUrl` if set, otherwise shows all looks. |
| Account icon | Opens Shopify customer login (`/account`). |
| Logo | Back to all looks. |

The cart and wishlist are stored in the visitor's browser, so they survive reloads.
The cart becomes a Shopify cart at checkout.
