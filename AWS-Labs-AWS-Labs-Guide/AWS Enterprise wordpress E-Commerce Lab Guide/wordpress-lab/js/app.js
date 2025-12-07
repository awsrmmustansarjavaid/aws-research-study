// Add to Cart
function addToCart(productId){
    fetch('api/cart.php', {
        method:'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: `product_id=${productId}&quantity=1`
    })
    .then(res=>res.json())
    .then(data => { alert(data.message); });
}

// Checkout
function checkout(){
    fetch('api/checkout.php', {method:'POST'})
    .then(res=>res.json())
    .then(data => { alert(data.message || data.error); });
}
