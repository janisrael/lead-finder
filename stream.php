<?php
header('Content-Type: text/event-stream');
header('Cache-Control: no-cache');
header('Connection: keep-alive');

function getNewPlaces($lastId) {
    $db = new PDO('sqlite:' . __DIR__ . '/places.db');
    $stmt = $db->prepare('SELECT * FROM places WHERE id > :lastId ORDER BY id ASC');
    $stmt->execute([':lastId' => $lastId]);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

$lastId = 0;

while (true) {
    // Trigger crawl to refresh the DB
    $url = 'http://127.0.0.1:5009/crawl?' . http_build_query($_GET);
    @file_get_contents($url);

    // Fetch new rows
    $newRows = getNewPlaces($lastId);

    if (!empty($newRows)) {
        echo "data: " . json_encode($newRows) . "\n\n";
        ob_flush();
        flush();
        $lastId = end($newRows)['id'];
    }

    sleep(5);
}
