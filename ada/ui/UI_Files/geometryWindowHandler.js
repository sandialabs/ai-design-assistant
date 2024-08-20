import * as THREE from './three.module.js';
import * as TWEEN from './tween.esm.js';
import { OrbitControls } from './OrbitControls.js'
import { STLLoader } from './STLLoader.js'

let threejsCanvas = document.getElementById("geometry-window-body")
let width = threejsCanvas.offsetWidth
let height = threejsCanvas.offsetHeight

const scene = new THREE.Scene()
const camera = new THREE.PerspectiveCamera(45,width/height,0.01,1000)
// const camera = new THREE.OrthographicCamera( width / - 200, width / 200, height / 200, height / - 200, 1, 1000 );
camera.position.set(10,10,10)
camera.lookAt(0,0,0)

const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
})
renderer.setSize(width,height)

const controls = new OrbitControls(camera, renderer.domElement)
// controls.zoomToCursor = true;
// controls.autoRotate = false;

controls.mouseButtons = {
    LEFT: THREE.MOUSE.ROTATE,
    // RIGHT: THREE.MOUSE.DOLLY,
    MIDDLE: THREE.MOUSE.PAN
}

renderer.setPixelRatio(Math.min(window.devicePixelRatio,2))
threejsCanvas.appendChild(renderer.domElement)

// Create a box
// const material = new THREE.MeshStandardMaterial({ color       : 0xff88ff , 
//                                                   transparent : false, 
//                                                   opacity     : 0.1,
//                                                   emissive    : 0x000000,
//                                                   flatShading : false,
//                                                   metalness   : 0.2,
//                                                   roughness   : 0.2,
//                                                   wireframe   : false,
//                                                   fog         : true,
//                                                   });

// const geometry = new THREE.BoxGeometry();
// const box = new THREE.Mesh(geometry, material);
// box.frustumCulled = false;
// scene.add(box);

// const loader = new STLLoader()
// loader.load(
//     './airfoil_flat.stl',
//     function (geometry) {
//         const mesh = new THREE.Mesh(geometry, material)
//         scene.add(mesh)
//     },
//     (xhr) => {
//         console.log((xhr.loaded / xhr.total) * 100 + '% loaded')
//     },
//     (error) => {
//         console.log(error)
//     }
// )

// // Create a sine-like wave
// const curve = new THREE.SplineCurve( [
//     new THREE.Vector2( -10, 0 ),
//     new THREE.Vector2( -5, 5 ),
//     new THREE.Vector2( 0, 0 ),
//     new THREE.Vector2( 5, -5 ),
//     new THREE.Vector2( 10, 0 )
// ] );

// const points = curve.getPoints( 50 );
// const geometry = new THREE.BufferGeometry().setFromPoints( points );

// const material = new THREE.LineBasicMaterial( {
//     color: 0x000000,
//     linewidth: 40,
//     linecap: 'round', //ignored by WebGLRenderer
//     linejoin:  'round' //ignored by WebGLRenderer
// } );

// // Create the final object to add to the scene
// const splineObject = new THREE.Line( geometry, material );
// scene.add(splineObject)


// Add ambient light to the scene
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

// Add directional light to the scene
const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
directionalLight.position.set(5, 5, -5);
scene.add(directionalLight);

const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
directionalLight2.position.set(-5, -5, -5);
scene.add(directionalLight2);

scene.add(new THREE.AxesHelper(5))
scene.traverse( function( object ) { object.frustumCulled = false; } )
// scene.frustumCulled = false;

// scene.fog.color(0xff0000)

// const light = new THREE.AmbientLight( 0x404040 ); // soft white light
// scene.add( light );

animate()

window.addEventListener('resize', onResize)

function animate() {
    // box.rotation.y += 0.01
    // mesh.rotation.y += 0.01
    window.requestAnimationFrame(animate)
    TWEEN.update(); // Update TWEEN animations
    renderer.render(scene,camera)
}

function onResize() {
    const windowHeight = window.innerHeight;
    const mainColumns = document.querySelectorAll('.main-column');
    mainColumns.forEach(col => {
    col.setAttribute('style','height:'+String(windowHeight-58)+'px')
    });

    // Resets the canvas to a smaller size so that the window div can flex
    renderer.setSize(100,100)

    // Do the expected thing
    let threejsCanvas = document.getElementById("geometry-window-body")
    let width = threejsCanvas.offsetWidth
    let height = threejsCanvas.offsetHeight
    renderer.setSize(width,height)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio,2))
    camera.aspect = width/height 
    camera.updateProjectionMatrix()
}

function moveCamera(targetPosition, duration) {
var tween = new TWEEN.Tween(camera.position)
  .to(targetPosition, duration)
  .easing(TWEEN.Easing.Quadratic.InOut)
  .onUpdate(function () {
    controls.update(); // Update controls during the tween
  })
  .start();
}

function rotateCamera(targetLookAt, duration) {
var tween = new TWEEN.Tween(controls.target)
  .to(targetLookAt, duration)
  .easing(TWEEN.Easing.Quadratic.InOut)
  .onUpdate(function () {
    controls.update(); // Update controls during the tween
  })
  .start();
}

function moveAndRotateCamera(targetPosition, targetLookAt, duration) {
    var positionTween = new TWEEN.Tween(camera.position)
      .to(targetPosition, duration/2.0)
      .easing(TWEEN.Easing.Quadratic.InOut)  
      .onUpdate(function () {
        controls.update(); // Update controls during the tween
      });

    var lookAtTween = new TWEEN.Tween(controls.target)
      .to(targetLookAt, duration/2.0)
      .easing(TWEEN.Easing.Quadratic.InOut)
      .onUpdate(function () {
        controls.update(); // Update controls during the tween
      });

    // Chain the tweens for position and lookAt
    positionTween.chain(lookAtTween);

    // Start the position tween, which will trigger the lookAt tween
    positionTween.start();
}

function clearObjects() {
// Iterate over all objects in the scene
scene.traverse(function (object) {
  if (object instanceof THREE.Mesh) {
    // Dispose of the object's geometry and material
    object.geometry.dispose();
    object.material.dispose();
  }
  if (object instanceof THREE.Line) {
    // Dispose of the object's geometry and material
    object.geometry.dispose();
    object.material.dispose();
  }
});

// Remove all objects from the scene
scene.children.length = 0;
}

function updateGraphicWindow(inputStructure) {
    // console.log('in graphic updater')

    if ("clear_objects" in inputStructure) {
        if (inputStructure.clear_objects == true) {
            clearObjects();
            scene.add(new THREE.AxesHelper(5))
        }
    }

    if ("new_stl_file" in inputStructure) {
        console.log(inputStructure.new_stl_file)
    }

    if ("new_camera_position" in inputStructure && "new_camera_target" in inputStructure) {
        moveAndRotateCamera({ x: inputStructure.new_camera_position[0], 
                              y: inputStructure.new_camera_position[1], 
                              z: inputStructure.new_camera_position[2] },
                            { x: inputStructure.new_camera_target[0], 
                              y: inputStructure.new_camera_target[1], 
                              z: inputStructure.new_camera_target[2] },
                              2000);
    }
    else if ("new_camera_position" in inputStructure) {
        moveCamera({ x: inputStructure.new_camera_position[0], 
                     y: inputStructure.new_camera_position[1], 
                     z: inputStructure.new_camera_position[2] },
                     1000);
    }
    else if ("new_camera_position" in inputStructure) {
        rotateCamera({ x: inputStructure.new_camera_position[0], 
                       y: inputStructure.new_camera_position[1], 
                       z: inputStructure.new_camera_position[2] },
                       1000);
    }
    else {
        // do nothing 
    }


    if ("curves" in inputStructure) {
        const line_material_black = new THREE.LineBasicMaterial( {
            color: 0x000000,
            linewidth: 1,
            linecap: 'round', //ignored by WebGLRenderer
            linejoin:  'round' //ignored by WebGLRenderer
        } );

        for (let i = 0; i < inputStructure.curves.length; i++) {
            const curveVectors = [];
            for (let j = 0; j < inputStructure.curves[i][0].length; j++) {
              curveVectors[j] = new THREE.Vector3(inputStructure.curves[i][0][j], inputStructure.curves[i][1][j], inputStructure.curves[i][2][j])
            }
            const geometry = new THREE.BufferGeometry().setFromPoints( curveVectors );
            const splineObject = new THREE.Line( geometry, line_material_black );
            scene.add(splineObject)

            const TE_points = [];
            TE_points[0] = new THREE.Vector3(inputStructure.curves[i][0][inputStructure.curves[i][0].length-1], 
                                             inputStructure.curves[i][1][inputStructure.curves[i][1].length-1], 
                                             inputStructure.curves[i][2][inputStructure.curves[i][2].length-1])
            TE_points[1] = new THREE.Vector3(inputStructure.curves[i][0][0], inputStructure.curves[i][1][0], inputStructure.curves[i][2][0])
            const geometry_teLine = new THREE.BufferGeometry().setFromPoints( TE_points );
            const teLine = new THREE.Line( geometry_teLine, line_material_black );
            scene.add(teLine)
        }
    }

    scene.traverse( function( object ) { object.frustumCulled = false; } );
}




export {updateGraphicWindow} ;
