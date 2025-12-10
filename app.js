let typeList = [];

const input = document.getElementById("typeText");
const tagsContainer = document.getElementById("typeTags");
const hiddenField = document.getElementById("typesField");
let x = 0;

input.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    e.preventDefault();
    const val = input.value.trim().toLowerCase().replace(/\s+/g, "_");
    if (val && !typeList.includes(val)) {
      typeList.push(val);
      updateTags();
    }
    input.value = "";
  }
});
function clearSelectedTypes() {
  typeList = [];
  updateTags();
}
function updateTags() {
  tagsContainer.innerHTML = "";
  typeList.forEach((type, index) => {
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = type.replace(/_/g, " ");

    const removeBtn = document.createElement("button");
    removeBtn.innerHTML = "×";
    removeBtn.onclick = () => {
      typeList.splice(index, 1);
      updateTags();
    };
    tag.appendChild(removeBtn);
    tagsContainer.appendChild(tag);
  });
  hiddenField.value = typeList.join(",");
}

const presetTypes = [
  "accounting",
  "airport",
  "amusement_park",
  "aquarium",
  "art_gallery",
  "atm",
  "bakery",
  "bank",
  "bar",
  "beauty_salon",
  "bicycle_store",
  "book_store",
  "bowling_alley",
  "bus_station",
  "cafe",
  "campground",
  "car_dealer",
  "car_rental",
  "car_repair",
  "car_wash",
  "casino",
  "cemetery",
  "church",
  "city_hall",
  "clothing_store",
  "convenience_store",
  "courthouse",
  "dentist",
  "department_store",
  "doctor",
  "drugstore",
  "electrician",
  "electronics_store",
  "embassy",
  "fire_station",
  "florist",
  "funeral_home",
  "furniture_store",
  "gas_station",
  "gym",
  "hair_care",
  "hardware_store",
  "hindu_temple",
  "home_goods_store",
  "hospital",
  "insurance_agency",
  "jewelry_store",
  "laundry",
  "lawyer",
  "library",
  "light_rail_station",
  "liquor_store",
  "local_government_office",
  "locksmith",
  "lodging",
  "meal_delivery",
  "meal_takeaway",
  "mosque",
  "movie_rental",
  "movie_theater",
  "moving_company",
  "museum",
  "night_club",
  "painter",
  "park",
  "parking",
  "pet_store",
  "pharmacy",
  "physiotherapist",
  "plumber",
  "police",
  "post_office",
  "primary_school",
  "real_estate_agency",
  "restaurant",
  "roofing_contractor",
  "rv_park",
  "school",
  "secondary_school",
  "shoe_store",
  "shopping_mall",
  "spa",
  "stadium",
  "storage",
  "store",
  "subway_station",
  "supermarket",
  "synagogue",
  "taxi_stand",
  "tourist_attraction",
  "train_station",
  "transit_station",
  "travel_agency",
  "university",
  "veterinary_care",
  "zoo",
];

const presetContainer = document.getElementById("presetTypes");
presetTypes.forEach((type) => {
  const btn = document.createElement("button");
  btn.textContent = type.replace(/_/g, " ");
  btn.type = "button";
  btn.className = "preset-btn";
  btn.onclick = () => {
    if (!typeList.includes(type)) {
      typeList.push(type);
      updateTags();
    }
  };
  presetContainer.appendChild(btn);
});

document.getElementById("typeSearch").addEventListener("input", function () {
  const filter = this.value.trim().toLowerCase();
  Array.from(presetContainer.children).forEach((button) => {
    const text = button.textContent.toLowerCase();
    button.style.display = text.includes(filter) ? "" : "none";
  });
});

const form = document.getElementById("searchForm");
const loadingOverlay = document.getElementById("loadingOverlay");
const tbody = document.querySelector("#resultsTable tbody");
let pollingInterval;

form.addEventListener("submit", (e) => {
  e.preventDefault();

  x = 0;
  tbody.innerHTML = "";
  if (pollingInterval) clearInterval(pollingInterval);

  loadingOverlay.style.display = "flex";

  hiddenField.value = typeList.join(",");

  const formData = new FormData(form);
  const params = new URLSearchParams(formData);
  
  // Start crawl
  fetch("/crawl?" + params.toString())
    .then(res => res.json())
    .then(data => {
      console.log("Crawl started:", data);
    })
    .catch(err => {
      console.error("Failed to start crawl:", err);
      loadingOverlay.style.display = "none";
    });

  // Poll for results using /stream endpoint
  let lastId = 0;
  let emptyCount = 0;
  const maxEmptyCount = 5; // Stop after 5 consecutive empty responses (10 seconds)
  
  pollingInterval = setInterval(async () => {
    try {
      const response = await fetch(`/stream?last_id=${lastId}`);
      if (!response.ok) throw new Error("Network error");
      const data = await response.json();
      console.log("Received batch:", data.results);

      if (data.results && data.results.length > 0) {
        console.log(`Adding ${data.results.length} results, lastId: ${data.last_id}`);
        emptyCount = 0; // Reset empty count when we get results
        x = x + data.results.length;
        document.getElementById("count").textContent = `Found ${x} leads`;
        document.getElementById("resultsTable").style.display = "table";

        data.results.forEach((biz) => {
          console.log("Adding business:", biz.name);
          appendRow(biz);
        });
        lastId = data.last_id;
      } else {
        emptyCount++;
        console.log(`No new results, lastId: ${lastId}, empty count: ${emptyCount}/${maxEmptyCount}`);
        
        // Stop polling after maxEmptyCount consecutive empty responses
        if (emptyCount >= maxEmptyCount) {
          console.log("Stopping polling - no new results for", maxEmptyCount * 2, "seconds");
          clearInterval(pollingInterval);
          loadingOverlay.style.display = "none";
        }
      }
    } catch (err) {
      console.error(err);
      emptyCount++;
      // Stop polling after maxEmptyCount consecutive errors
      if (emptyCount >= maxEmptyCount) {
        console.log("Stopping polling due to errors");
        clearInterval(pollingInterval);
        loadingOverlay.style.display = "none";
      }
    }
  }, 2000);
});

function appendRow(biz) {
  const idx = tbody.rows.length + 1;
  const typesStr = (biz.types || [])
    .map((t) => t.replace(/_/g, " "))
    .join(", ");

  const tr = document.createElement("tr");

  function createTd(content) {
    const td = document.createElement("td");
    if (typeof content === "string") {
      td.textContent = content;
    } else if (content instanceof HTMLElement) {
      td.appendChild(content);
    }
    return td;
  }

  let websiteCellContent;
  if (biz.website) {
    const a = document.createElement("a");
    a.href = biz.website;
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = "Website";
    websiteCellContent = a;
  } else {
    websiteCellContent = "N/A";
  }

  tr.appendChild(createTd(idx.toString()));
  tr.appendChild(createTd(biz.name || ""));
  tr.appendChild(createTd(biz.address || ""));
  tr.appendChild(createTd(biz.phone || ""));
  tr.appendChild(createTd(websiteCellContent));
  tr.appendChild(createTd(biz.rating != null ? biz.rating.toString() : ""));
  tr.appendChild(createTd(typesStr));
  tr.appendChild(createTd(biz.status || ""));

  tbody.appendChild(tr);
}

document.getElementById("exportBtn").addEventListener("click", () => {
  const table = document.getElementById("resultsTable");
  const rows = Array.from(table.querySelectorAll("tr"));

  let csvContent = "";
  rows.forEach((row) => {
    const cols = Array.from(row.querySelectorAll("th, td")).map((col) => {
      let text = "";
      if (col.querySelector("a")) {
        text = col.querySelector("a").href;
      } else {
        text = col.textContent || "";
      }
      text = text.replace(/"/g, '""');
      return `"${text}"`;
    });
    csvContent += cols.join(",") + "\n";
  });

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const timestamp = new Date()
    .toISOString()
    .replace(/[:T]/g, "-")
    .replace(/\..+/, "");
  const filename = `businesses_${timestamp}.csv`;

  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
});

document.getElementById("radius").addEventListener("input", () => {
  updateCircle();
});

let map;
let marker;
let radiusCircle;
let selectedLatLng;

function initMap() {
  const defaultLatLng = { lat: 50.0405, lng: -110.6766 };
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 10,
    center: defaultLatLng,
  });

  const input = document.getElementById("mapSearchBox");
  const searchBox = new google.maps.places.SearchBox(input);

  map.addListener("bounds_changed", () => {
    searchBox.setBounds(map.getBounds());
  });

  map.addListener("click", (e) => {
    selectedLatLng = e.latLng;
    placeMarker(selectedLatLng);
    updateLocationInput(selectedLatLng);
    updateCircle(); // draw/update radius
  });

  searchBox.addListener("places_changed", () => {
    const places = searchBox.getPlaces();
    if (places.length === 0) return;

    const place = places[0];
    if (!place.geometry || !place.geometry.location) return;

    selectedLatLng = place.geometry.location;
    placeMarker(selectedLatLng);
    map.panTo(selectedLatLng);
    map.setZoom(15);
    updateLocationInput(selectedLatLng);
    updateCircle(); // draw/update radius
  });
}

function openMap() {
  document.getElementById("mapModal").style.display = "block";
  if (!map) initMap();
}

function closeMap() {
  document.getElementById("mapModal").style.display = "none";
}

function placeMarker(latlng) {
  if (!marker) {
    marker = new google.maps.Marker({
      position: latlng,
      map: map,
      draggable: true,
    });


    marker.addListener("dragend", function () {
      const newPosition = marker.getPosition();
      selectedLatLng = newPosition;
      updateLocationInput(newPosition);
      updateCircle();
    });
  } else {
    marker.setPosition(latlng);
  }
}

function updateLocationInput(latlng) {
  document.getElementById("locationInput").value = `${latlng
    .lat()
    .toFixed(6)},${latlng.lng().toFixed(6)}`;
}


function updateCircle() {
  const radiusKm = parseFloat(document.getElementById("radius").value) || 10;
  const radiusMeters = radiusKm * 1000;

  if (radiusCircle) {
    radiusCircle.setMap(null);
  }

  if (!selectedLatLng) return;

  radiusCircle = new google.maps.Circle({
    strokeColor: "#4285F4",
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: "#4285F4",
    fillOpacity: 0.2,
    map,
    center: selectedLatLng,
    radius: radiusMeters,
  });
}

// function updateLocationInput(latlng) {
//   document.getElementById("locationInput").value = `${latlng.lat().toFixed(6)},${latlng.lng().toFixed(6)}`;
// }
