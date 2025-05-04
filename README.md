# Flight Information System for Airport Blackouts -- Blackout Challenge

## Introduction

During an airport blackout, traditional flight information displays and communication systems may fail, leaving travelers in the dark about critical flight details. This project is a **flight information system designed for use during airport blackouts**. It allows passengers to retrieve up-to-date flight information (departures, arrivals, gates, status, etc.) by connecting to a local Wi-Fi network served by our system. Built during **UPC Hackathon 2025**, the solution focuses on resilience and accessibility, ensuring that even when the lights go out, important flight data remains available to everyone.

## Objectives

* **Provide Critical Flight Data Offline:** Deliver essential flight information (departure and arrival times, gate numbers, flight status, baggage claim belts, etc.) to travelers without reliance on the airport’s main power or internet infrastructure.
* **Lightweight Wi-Fi Network for Travelers:** Use a local Wi-Fi access point to broadcast a web page that travelers can easily connect to with a smartphone or laptop. No app installation or mobile data is required – just connect and view in a browser.
* **Resilient and Easy to Deploy:** Design the system to run on minimal hardware (e.g., Raspberry Pis with battery backup) and form a network that can cover key areas of an airport during emergencies. The system should be simple to set up quickly in a crisis situation.

## Initial Design

Our initial design proposed a network of Raspberry Pi devices forming an **ad-hoc mesh network** throughout the airport. Each Raspberry Pi node would fetch flight data from online APIs and then share or sync this data with other nodes locally. This decentralized approach was intended to ensure that:

1. **Coverage:** Multiple nodes could be placed around the airport (e.g., at different terminals or gates) to extend Wi-Fi coverage, so travelers anywhere in the airport could connect to the nearest node.
2. **Redundancy:** By syncing data across nodes, if one node went down, others would still hold the flight information and continue serving users.
3. **Local Data Consistency:** All nodes would maintain the same up-to-date flight dataset, obtained from external sources and then propagated within the mesh, so that a traveler sees consistent information regardless of which node they connect to.

For data sources, we explored several APIs to gather real-time flight information. We initially tested the **OpenSky Network API** and **AviationStack API**, hoping to obtain live flight status and schedule details. The plan was to use these APIs to continuously pull flight updates (arrival/departure times, delays, etc.) and then distribute that data among the Raspberry Pis in the mesh.

## Challenges

We encountered a number of challenges that forced us to pivot from the original mesh-network concept:

* **Network Hardware Limitations:** While we had multiple Raspberry Pis available, we lacked the network hardware to link them. We had no network switch or direct Ethernet cables to wire the Pis together. Relying on wireless alone proved difficult due to configuration and stability issues under time constraints.
* **Infrastructure Constraints:** Using existing Wi-Fi networks at the venue was not viable. The university’s Wi-Fi has client isolation (devices on the network cannot see each other), preventing our Pis from communicating or forming any local mesh. We also tried using a smartphone hotspot to connect devices, but many phone hotspots disconnect clients that are idle for too long, which disrupted the persistence of our network.
* **Ad-Hoc Networking Complexity:** Setting up an ad-hoc or mesh Wi-Fi network between Raspberry Pis (without any router or internet) is complex and time-consuming. Within the hackathon’s limited timeframe, configuring a stable mesh protocol and ensuring all nodes sync correctly proved too ambitious given the other challenges.
* **API Data Limitations:** The flight data APIs we tested had their own limitations. For example, the OpenSky API is great for live aircraft data but didn’t easily provide scheduled gate/terminal information. AviationStack offered general flight data, but the free tier lacked key information like gates and baggage belts, which are critical during a blackout.

## Final Solution

After encountering issues with API limitations and network infrastructure constraints, we opted for two complementary approaches to demonstrate the core idea of a blackout-resilient flight information system:

### 🛬 1. Web Scraping from AENA for Real Flight Data

To obtain **reliable and detailed flight information**, we implemented a **web scraper** targeting the official AENA "Infovuelos" website for **Barcelona-El Prat Airport (LEBL)**. This was the only free method that provided the full range of critical data needed during a blackout:

* Departure and arrival times
* Flight numbers and airline
* Gate (boarding gate / puerta de embarque)
* Baggage belt and sala
* Terminal
* Flight status (boarding, landed, delayed, etc.)

The scraper parses the HTML structure of the page and extracts relevant data from both **departure** and **arrival** tables. It then filters flights to show only those occurring in the next few hours, keeping the dataset lightweight and focused.

This scraped information can be transformed into a static or dynamic web page, and served from any local server or device (e.g., Raspberry Pi, laptop, or local web appliance) during an outage. It guarantees up-to-date, critical data with no external API limitations or authentication hassles.

### 📡 2. Raspberry Pi Access Point with Minimal Web Server

To simulate a localized emergency information system, we configured a **Raspberry Pi** to operate as an **access point (AP)** and web server:

* The Pi uses `hostapd` and `dnsmasq` to create a **local Wi-Fi network** (no Internet).
* When users connect to this network, they're redirected to a **simple static dashboard** hosted by `lighttpd`.
* The HTML interface is minimal and responsive, showing basic flight info pulled from the **AviationStack API**, such as:

  * Flight ID
  * Departure date
  * Origin and destination
  * Last update timestamp

The goal of this interface is to **simulate the user experience** of a blackout: accessing flight info without Internet, through a local access point in the airport.

This version is intentionally limited due to the constraints of free API tiers (AviationStack), which do not provide critical fields like boarding gates or baggage belts. However, it demonstrates the **network and delivery mechanism** in a blackout context.

## Intended Vision

While our final solution includes a working scraping system and a simulated API-based access point, our **original goal remains unchanged**: to implement a real distributed system based on Raspberry Pis working together as a mesh or coordinated local network.

Given more time and hardware access, we would deploy:

* Multiple Raspberry Pis across an airport environment
* Peer-to-peer synchronization of flight data
* Seamless handoff of user traffic across nodes
* Decentralized architecture with offline caching and battery resilience

## Conclusion

This project shows that even in a full infrastructure failure scenario, passengers can stay informed through lightweight, resilient, and independent systems. Whether using scraped local data or API-sourced dashboards, our solution ensures **access to the most critical information when it's needed most**. It represents a first step toward a robust, scalable emergency flight info system that any airport could adopt.
