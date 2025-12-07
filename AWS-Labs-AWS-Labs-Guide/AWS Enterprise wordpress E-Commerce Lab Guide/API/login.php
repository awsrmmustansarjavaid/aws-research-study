<?php
require_once('wp-load.php');
header('Content-Type: application/json');

$username = $_POST['username'];
$password = $_POST['password'];

$user = wp_signon(array(
    'user_login' => $username,
    'user_password' => $password,
    'remember' => true
));

if (is_wp_error($user)) {
    echo json_encode(array('error' => $user->get_error_message()));
} else {
    echo json_encode(array('message' => 'Login successful', 'user_id' => $user->ID));
}
?>
