/**
 * Cerca - İstemci Taraflı Arama ve Konum Bazlı Mesafe Motoru (Proximity Engine)
 */

document.addEventListener('DOMContentLoaded', () => {
  initQuickSearch();
});

// 1. Şehir Değiştirme
function cercaChangeCity(citySlug) {
  if (!citySlug) return;
  if (citySlug === 'tum-sehirler') {
    window.location.href = '/sehirler/';
  } else {
    window.location.href = `/sehir/${citySlug}/`;
  }
}

// 2. Canlı Hızlı Arama
function initQuickSearch() {
  const input = document.getElementById('cercaQuickSearch');
  const heroInput = document.getElementById('cercaHeroSearch');
  
  const setupInput = (el) => {
    if (!el) return;
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const query = el.value.trim();
        if (query) {
          window.location.href = `/ara/?q=${encodeURIComponent(query)}`;
        }
      }
    });
  };

  setupInput(input);
  setupInput(heroInput);
}

// 3. Konum Bazlı Mesafe Hesaplama (Haversine Formülü)
function calculateDistanceKm(lat1, lon1, lat2, lon2) {
  const R = 6371; // Dünya yarıçapı km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return Math.round(R * c * 10) / 10;
}

// 4. "Yakınımdakiler" GPS Butonu
function cercaFindNearMe() {
  if (!navigator.geolocation) {
    alert("Tarayıcınız konum servisini desteklemiyor. Lütfen şehir seçiniz.");
    return;
  }

  const btn = document.querySelector('.cerca-btn-nearme');
  if (btn) {
    btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> <span>Aranıyor...</span>`;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const userLat = position.coords.latitude;
      const userLon = position.coords.longitude;
      sessionStorage.setItem('cerca_user_lat', userLat);
      sessionStorage.setItem('cerca_user_lon', userLon);

      if (btn) {
        btn.innerHTML = `<i class="fas fa-check"></i> <span>Konum Alındı</span>`;
      }

      // Yakındaki mekanlar/etkinlikler sayfasına yönlendir
      window.location.href = `/yakindaki-etkinlikler/?lat=${userLat}&lon=${userLon}`;
    },
    (error) => {
      console.warn("Konum izni verilmedi:", error.message);
      if (btn) {
        btn.innerHTML = `<i class="fas fa-location-arrow"></i> <span>Yakınımdakiler</span>`;
      }
      alert("Yakınınızdaki etkinlikleri listelemek için konum iznine ihtiyaç duyulmaktadır. İstanbul etkinlikleri gösteriliyor.");
      window.location.href = "/sehir/istanbul/";
    },
    { timeout: 10000, enableHighAccuracy: true }
  );
}
