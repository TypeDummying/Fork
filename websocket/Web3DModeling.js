
// Web3DModeling.js
// This module provides web-based 3D modeling tools for the Fork 3D modeling software

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { TransformControls } from 'three/examples/jsm/controls/TransformControls';
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter';

class Web3DModeling {
    constructor(container) {
        this.container = container;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.transformControls = null;
        this.objects = [];
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.selectedObject = null;

        this.init();
    }

    /**
     * Initialize the 3D environment
     */
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf0f0f0);

        // Create camera
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 5, 10);

        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.container.appendChild(this.renderer.domElement);

        // Add orbit controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.damping = 0.2;

        // Add transform controls
        this.transformControls = new TransformControls(this.camera, this.renderer.domElement);
        this.transformControls.addEventListener('dragging-changed', (event) => {
            this.controls.enabled = !event.value;
        });
        this.scene.add(this.transformControls);

        // Add lights
        const ambientLight = new THREE.AmbientLight(0x404040);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(1, 1, 1);
        this.scene.add(directionalLight);

        // Add grid helper
        const gridHelper = new THREE.GridHelper(10, 10);
        this.scene.add(gridHelper);

        // Add event listeners
        window.addEventListener('resize', this.onWindowResize.bind(this), false);
        this.renderer.domElement.addEventListener('mousedown', this.onMouseDown.bind(this), false);
        this.renderer.domElement.addEventListener('mousemove', this.onMouseMove.bind(this), false);

        // Start animation loop
        this.animate();
    }

    /**
     * Animation loop
     */
    animate() {
        requestAnimationFrame(this.animate.bind(this));
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Handle window resize
     */
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    /**
     * Handle mouse down event
     * @param {MouseEvent} event 
     */
    onMouseDown(event) {
        event.preventDefault();

        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.camera);

        const intersects = this.raycaster.intersectObjects(this.objects, true);

        if (intersects.length > 0) {
            this.selectedObject = intersects[0].object;
            this.transformControls.attach(this.selectedObject);
        } else {
            this.selectedObject = null;
            this.transformControls.detach();
        }
    }

    /**
     * Handle mouse move event
     * @param {MouseEvent} event 
     */
    onMouseMove(event) {
        event.preventDefault();

        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    }

    /**
     * Add a new object to the scene
     * @param {string} type - Type of object to add (cube, sphere, cylinder)
     * @param {Object} params - Parameters for the object
     */
    addObject(type, params = {}) {
        let geometry, material, object;

        switch (type) {
            case 'cube':
                geometry = new THREE.BoxGeometry(
                    params.width || 1,
                    params.height || 1,
                    params.depth || 1
                );
                break;
            case 'sphere':
                geometry = new THREE.SphereGeometry(
                    params.radius || 0.5,
                    params.widthSegments || 32,
                    params.heightSegments || 32
                );
                break;
            case 'cylinder':
                geometry = new THREE.CylinderGeometry(
                    params.radiusTop || 0.5,
                    params.radiusBottom || 0.5,
                    params.height || 1,
                    params.radialSegments || 32
                );
                break;
            default:
                console.error('Invalid object type');
                return;
        }

        material = new THREE.MeshPhongMaterial({
            color: params.color || 0xffffff,
            flatShading: params.flatShading || false,
        });

        object = new THREE.Mesh(geometry, material);
        object.position.set(params.x || 0, params.y || 0, params.z || 0);
        this.scene.add(object);
        this.objects.push(object);
    }

    /**
     * Remove an object from the scene
     * @param {THREE.Object3D} object - Object to remove
     */
    removeObject(object) {
        const index = this.objects.indexOf(object);
        if (index !== -1) {
            this.objects.splice(index, 1);
            this.scene.remove(object);
            if (this.selectedObject === object) {
                this.selectedObject = null;
                this.transformControls.detach();
            }
        }
    }

    /**
     * Clear all objects from the scene
     */
    clearScene() {
        while (this.objects.length > 0) {
            this.removeObject(this.objects[0]);
        }
    }

    /**
     * Export the scene to GLTF format
     * @returns {Promise<ArrayBuffer>} - The exported GLTF data
     */
    exportToGLTF() {
        return new Promise((resolve, reject) => {
            const exporter = new GLTFExporter();
            exporter.parse(this.scene, (gltf) => {
                resolve(gltf);
            }, { binary: true });
        });
    }

    /**
     * Export the scene to OBJ format
     * @returns {string} - The exported OBJ data
     */
    exportToOBJ() {
        const exporter = new OBJExporter();
        return exporter.parse(this.scene);
    }

    /**
     * Import a 3D model from a file
     * @param {File} file - The file to import
     * @returns {Promise<void>}
     */
    importModel(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (event) => {
                const contents = event.target.result;
                const extension = file.name.split('.').pop().toLowerCase();

                let loader;

                switch (extension) {
                    case 'gltf':
                    case 'glb':
                        loader = new THREE.GLTFLoader();
                        break;
                    case 'obj':
                        loader = new THREE.OBJLoader();
                        break;
                    default:
                        reject(new Error('Unsupported file format'));
                        return;
                }

                loader.load(contents, (object) => {
                    this.scene.add(object.scene || object);
                    this.objects.push(object.scene || object);
                    resolve();
                }, undefined, reject);
            };
            reader.readAsDataURL(file);
        });
    }

    /**
     * Apply a material to the selected object
     * @param {Object} params - Material parameters
     */
    applyMaterial(params) {
        if (!this.selectedObject) {
            console.error('No object selected');
            return;
        }

        const material = new THREE.MeshPhongMaterial({
            color: params.color || 0xffffff,
            flatShading: params.flatShading || false,
            transparent: params.transparent || false,
            opacity: params.opacity || 1,
            wireframe: params.wireframe || false,
        });

        this.selectedObject.material = material;
    }

    /**
     * Apply a texture to the selected object
     * @param {string} textureUrl - URL of the texture image
     */
    applyTexture(textureUrl) {
        if (!this.selectedObject) {
            console.error('No object selected');
            return;
        }

        const textureLoader = new THREE.TextureLoader();
        textureLoader.load(textureUrl, (texture) => {
            const material = new THREE.MeshPhongMaterial({ map: texture });
            this.selectedObject.material = material;
        });
    }

    /**
     * Perform a boolean operation on two objects
     * @param {string} operation - Type of boolean operation (union, subtract, intersect)
     * @param {THREE.Mesh} objectA - First object
     * @param {THREE.Mesh} objectB - Second object
     */
    booleanOperation(operation, objectA, objectB) {
        // Note: This is a placeholder. Actual boolean operations require a CSG library.
 /**/}}