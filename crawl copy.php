<?php
header('Content-Type: application/json');

$API_KEY = 'AIzaSyCAwaDlQXvVJ5H03aWHR8-WJ3zlvPPltws'; // Replace with your valid key
$location = $_GET['location'] ?? '50.0405,-110.6766';
$radius_km = floatval($_GET['radius'] ?? 20);
$radius = min(intval($radius_km * 1000), 50000); // max 50,000 meters allowed by API
$types = isset($_GET['types']) ? explode(',', $_GET['types']) : ['bakery','restaurant'];
$has_website = $_GET['has_website'] ?? 'both';

$hw = null;
if ($has_website === 'yes') $hw = true;
elseif ($has_website === 'no') $hw = false;

function get_details($api_key, $place_id) {
    $url = "https://maps.googleapis.com/maps/api/place/details/json?" . http_build_query([
        'key' => $api_key,
        'place_id' => $place_id,
        'fields' => 'website,formatted_phone_number'
    ]);
    $resp = file_get_contents($url);
    if ($resp === false) {
        return [null, null];
    }
    $data = json_decode($resp, true);
    if (!isset($data['result'])) return [null, null];
    return [
        $data['result']['website'] ?? null,
        $data['result']['formatted_phone_number'] ?? null
    ];
}

session_start();

$debug = [];

$hash = md5(serialize([$location, $radius, $types, $has_website]));
if (!isset($_SESSION['crawl']) || $_SESSION['crawl']['hash'] !== $hash) {
    $_SESSION['crawl'] = [
        'hash' => $hash,
        'types' => $types,
        'type_index' => 0,
        'next_page_token' => null,
        'done' => false,
        'results' => []
    ];
    $debug[] = "Session reset due to new query.";
}
$cx = &$_SESSION['crawl'];

if ($cx['done']) {
    echo json_encode(['done' => true, 'results' => [], 'debug' => ['All done, no more data']]);
    exit;
}

$currentType = $cx['types'][$cx['type_index']];
$debug[] = "Current type: $currentType";

if ($cx['next_page_token']) {
    $params = [
        'key' => $API_KEY,
        'pagetoken' => $cx['next_page_token']
    ];
    $debug[] = "Using next_page_token: " . $cx['next_page_token'];
    sleep(2);
} else {
    // $params = [
    //     'key' => $API_KEY,
    //     'location' => $location,
    //     'radius' => $radius,
    //     'type' => $currentType
    // ];
    $params = [
        'key' => $API_KEY,
        'location' => $location,
        'radius' => $radius,
        'keyword' => $currentType
    ];
    $debug[] = "Initial search parameters set";
}

$url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?' . http_build_query($params);
$debug[] = "Request URL: $url";

$res_json = @file_get_contents($url);
if ($res_json === false) {
    echo json_encode(['done' => true, 'results' => [], 'debug' => ['Error fetching Places API']]);
    exit;
}

$res = json_decode($res_json, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    echo json_encode(['done' => true, 'results' => [], 'debug' => ['JSON decode error: ' . json_last_error_msg()]]);
    exit;
}

if (!isset($res['results'])) {
    echo json_encode(['done' => true, 'results' => [], 'debug' => ['No results in API response']]);
    exit;
}

$new_results = [];
foreach ($res['results'] as $p) {
    list($website, $phone) = get_details($API_KEY, $p['place_id']);
    if ($hw !== null && $hw !== (!empty($website))) continue;

    $new_results[] = [
        'name' => $p['name'],
        'address' => $p['vicinity'] ?? '',
        'phone' => $phone,
        'website' => $website,
        'rating' => $p['rating'] ?? null,
        'types' => $p['types'] ?? [],
        'status' => $p['business_status'] ?? ''
    ];
    $debug[] = "Found: {$p['name']} ({$p['vicinity']})";
}

$cx['results'] = array_merge($cx['results'], $new_results);

if (!empty($res['next_page_token'])) {
    $cx['next_page_token'] = $res['next_page_token'];
    $debug[] = "Next page token found: " . $cx['next_page_token'];
} else {
    $cx['type_index']++;
    $cx['next_page_token'] = null;

    if ($cx['type_index'] >= count($cx['types'])) {
        $cx['done'] = true;
        $debug[] = "All types processed, done set to true.";
    } else {
        $debug[] = "Moving to next type index: " . $cx['type_index'];
    }
}

echo json_encode(['done' => $cx['done'], 'results' => $new_results, 'debug' => $debug]);
