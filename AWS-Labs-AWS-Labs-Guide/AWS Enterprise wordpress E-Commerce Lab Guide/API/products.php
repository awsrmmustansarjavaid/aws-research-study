<?php
// Example: Return list of products
require_once('wp-load.php');

header('Content-Type: application/json');

$args = array(
    'post_type' => 'product',
    'posts_per_page' => 10
);

$loop = new WP_Query($args);
$products = array();

while ($loop->have_posts()) : $loop->the_post();
    global $product;
    $products[] = array(
        'id' => $product->get_id(),
        'name' => $product->get_name(),
        'price' => $product->get_price(),
        'link' => get_permalink($product->get_id())
    );
endwhile;

echo json_encode($products);
?>
