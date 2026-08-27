(function() {
  var container = document.getElementById('visual-canvas');
  if (!container || typeof THREE === 'undefined') return;
  
  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
  var renderer = new THREE.WebGLRenderer({ canvas: container, alpha: true, antialias: true });
  
  function resize() {
    var section = document.getElementById('visual-section');
    if (!section) return;
    var width = section.clientWidth;
    var height = section.clientHeight;
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }
  window.addEventListener('resize', resize);
  resize();
  
  // Create an "AI Network Graph" using an Icosahedron
  var geometry = new THREE.IcosahedronGeometry(2, 2);
  
  // Wireframe material for the edges
  var wireframeMaterial = new THREE.LineBasicMaterial({ color: 0x34d399, transparent: true, opacity: 0.4 });
  var wireframe = new THREE.LineSegments(new THREE.WireframeGeometry(geometry), wireframeMaterial);
  
  // Points material for the nodes
  var pointsMaterial = new THREE.PointsMaterial({ color: 0xfbbf24, size: 0.15, transparent: true, opacity: 0.8 });
  var points = new THREE.Points(geometry, pointsMaterial);
  
  scene.add(wireframe);
  scene.add(points);
  
  camera.position.z = 5;
  
  // Interactive mouse rotation
  var mouseX = 0;
  var mouseY = 0;
  var targetX = 0;
  var targetY = 0;
  var windowHalfX = window.innerWidth / 2;
  var windowHalfY = window.innerHeight / 2;
  
  document.addEventListener('mousemove', function(event) {
    mouseX = (event.clientX - windowHalfX);
    mouseY = (event.clientY - windowHalfY);
  });
  
  function animate() {
    requestAnimationFrame(animate);
    
    targetX = mouseX * .001;
    targetY = mouseY * .001;
    
    wireframe.rotation.y += 0.05 * (targetX - wireframe.rotation.y);
    wireframe.rotation.x += 0.05 * (targetY - wireframe.rotation.x);
    wireframe.rotation.z += 0.005;
    
    points.rotation.y = wireframe.rotation.y;
    points.rotation.x = wireframe.rotation.x;
    points.rotation.z = wireframe.rotation.z;
    
    renderer.render(scene, camera);
  }
  animate();
})();
