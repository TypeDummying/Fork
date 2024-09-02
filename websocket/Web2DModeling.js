
// Web2DModeling.js
// This module provides web-based 2D modeling tools for the Fork 3D modeling software

/**
 * @class Web2DModeling
 * @description Handles 2D modeling operations in a web environment for Fork 3D modeling software
 */
class Web2DModeling {
    /**
     * @constructor
     * @param {Object} canvas - The HTML canvas element for rendering
     * @param {Object} options - Configuration options for the 2D modeling tools
     */
    constructor(canvas, options = {}) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.options = {
            strokeColor: options.strokeColor || '#000000',
            fillColor: options.fillColor || '#FFFFFF',
            lineWidth: options.lineWidth || 2,
            snapToGrid: options.snapToGrid || false,
            gridSize: options.gridSize || 10,
            ...options
        };

        this.shapes = [];
        this.currentShape = null;
        this.isDrawing = false;
        this.selectedShape = null;

        this.initEventListeners();
    }

    /**
     * @method initEventListeners
     * @description Initialize event listeners for user interactions
     */
    initEventListeners() {
        this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        this.canvas.addEventListener('dblclick', this.handleDoubleClick.bind(this));
    }

    /**
     * @method handleMouseDown
     * @param {Event} event - The mouse event
     * @description Handle mouse down event to start drawing or select a shape
     */
    handleMouseDown(event) {
        const { offsetX, offsetY } = event;
        const point = this.snapToGrid({ x: offsetX, y: offsetY });

        if (this.selectedShape) {
            this.deselectShape();
        }

        const clickedShape = this.getShapeAtPoint(point);
        if (clickedShape) {
            this.selectShape(clickedShape);
        } else {
            this.startDrawing(point);
        }
    }

    /**
     * @method handleMouseMove
     * @param {Event} event - The mouse event
     * @description Handle mouse move event to update the current shape being drawn or move a selected shape
     */
    handleMouseMove(event) {
        const { offsetX, offsetY } = event;
        const point = this.snapToGrid({ x: offsetX, y: offsetY });

        if (this.isDrawing) {
            this.updateCurrentShape(point);
        } else if (this.selectedShape) {
            this.moveSelectedShape(point);
        }

        this.render();
    }

    /**
     * @method handleMouseUp
     * @description Handle mouse up event to finish drawing or moving a shape
     */
    handleMouseUp() {
        if (this.isDrawing) {
            this.finishDrawing();
        } else if (this.selectedShape) {
            this.finishMovingShape();
        }
    }

    /**
     * @method handleDoubleClick
     * @param {Event} event - The mouse event
     * @description Handle double click event to edit a shape's properties
     */
    handleDoubleClick(event) {
        const { offsetX, offsetY } = event;
        const point = this.snapToGrid({ x: offsetX, y: offsetY });

        const clickedShape = this.getShapeAtPoint(point);
        if (clickedShape) {
            this.editShapeProperties(clickedShape);
        }
    }

    /**
     * @method snapToGrid
     * @param {Object} point - The point to snap to the grid
     * @returns {Object} The snapped point
     * @description Snap a point to the nearest grid intersection if snapToGrid is enabled
     */
    snapToGrid(point) {
        if (!this.options.snapToGrid) {
            return point;
        }

        return {
            x: Math.round(point.x / this.options.gridSize) * this.options.gridSize,
            y: Math.round(point.y / this.options.gridSize) * this.options.gridSize
        };
    }

    /**
     * @method getShapeAtPoint
     * @param {Object} point - The point to check for shape intersection
     * @returns {Object|null} The shape at the given point, or null if no shape is found
     * @description Find a shape that intersects with the given point
     */
    getShapeAtPoint(point) {
        for (let i = this.shapes.length - 1; i >= 0; i--) {
            if (this.shapes[i].containsPoint(point)) {
                return this.shapes[i];
            }
        }
        return null;
    }

    /**
     * @method selectShape
     * @param {Object} shape - The shape to select
     * @description Select a shape and highlight it
     */
    selectShape(shape) {
        this.selectedShape = shape;
        shape.isSelected = true;
        this.render();
    }

    /**
     * @method deselectShape
     * @description Deselect the currently selected shape
     */
    deselectShape() {
        if (this.selectedShape) {
            this.selectedShape.isSelected = false;
            this.selectedShape = null;
            this.render();
        }
    }

    /**
     * @method startDrawing
     * @param {Object} startPoint - The starting point for drawing
     * @description Start drawing a new shape
     */
    startDrawing(startPoint) {
        this.isDrawing = true;
        this.currentShape = new Rectangle(startPoint, { width: 0, height: 0 }, this.options);
    }

    /**
     * @method updateCurrentShape
     * @param {Object} endPoint - The current end point for the shape being drawn
     * @description Update the dimensions of the shape being drawn
     */
    updateCurrentShape(endPoint) {
        if (this.currentShape instanceof Rectangle) {
            const width = endPoint.x - this.currentShape.position.x;
            const height = endPoint.y - this.currentShape.position.y;
            this.currentShape.setDimensions({ width, height });
        }
    }

    /**
     * @method finishDrawing
     * @description Finish drawing the current shape and add it to the shapes array
     */
    finishDrawing() {
        if (this.currentShape) {
            this.shapes.push(this.currentShape);
            this.currentShape = null;
            this.isDrawing = false;
            this.render();
        }
    }

    /**
     * @method moveSelectedShape
     * @param {Object} newPosition - The new position for the selected shape
     * @description Move the selected shape to a new position
     */
    moveSelectedShape(newPosition) {
        if (this.selectedShape) {
            this.selectedShape.move(newPosition);
        }
    }

    /**
     * @method finishMovingShape
     * @description Finish moving the selected shape
     */
    finishMovingShape() {
        // Implement any necessary logic after moving a shape
    }

    /**
     * @method editShapeProperties
     * @param {Object} shape - The shape to edit
     * @description Open a dialog to edit the properties of a shape
     */
    editShapeProperties(shape) {
        // Implement a dialog or form to edit shape properties
        console.log('Editing properties for shape:', shape);
    }

    /**
     * @method render
     * @description Render all shapes on the canvas
     */
    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        if (this.options.snapToGrid) {
            this.drawGrid();
        }

        for (const shape of this.shapes) {
            shape.draw(this.ctx);
        }

        if (this.currentShape) {
            this.currentShape.draw(this.ctx);
        }
    }

    /**
     * @method drawGrid
     * @description Draw the grid on the canvas
     */
    drawGrid() {
        this.ctx.save();
        this.ctx.strokeStyle = '#CCCCCC';
        this.ctx.lineWidth = 0.5;

        for (let x = 0; x <= this.canvas.width; x += this.options.gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }

        for (let y = 0; y <= this.canvas.height; y += this.options.gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }

        this.ctx.restore();
    }

    /**
     * @method exportToSVG
     * @returns {string} The SVG representation of the drawing
     * @description Export the current drawing as an SVG string
     */
    exportToSVG() {
        let svg = `<svg width="${this.canvas.width}" height="${this.canvas.height}" xmlns="http://www.w3.org/2000/svg">`;

        for (const shape of this.shapes) {
            svg += shape.toSVG();
        }

        svg += '</svg>';
        return svg;
    }

    /**
     * @method importFromSVG
     * @param {string} svgString - The SVG string to import
     * @description Import shapes from an SVG string
     */
    importFromSVG(svgString) {
        const parser = new DOMParser();
        const svgDoc = parser.parseFromString(svgString, 'image/svg+xml');
        const svgElement = svgDoc.documentElement;

        this.shapes = [];

        const rectangles = svgElement.getElementsByTagName('rect');
        for (const rect of rectangles) {
            const x = parseFloat(rect.getAttribute('x'));
            const y = parseFloat(rect.getAttribute('y'));
            const width = parseFloat(rect.getAttribute('width'));
            const height = parseFloat(rect.getAttribute('height'));

            const shapeOptions = {
                strokeColor: rect.getAttribute('stroke') || this.options.strokeColor,
                fillColor: rect.getAttribute('fill') || this.options.fillColor,
                lineWidth: parseFloat(rect.getAttribute('stroke-width')) || this.options.lineWidth
            };

            const rectangle = new Rectangle({ x, y }, { width, height }, shapeOptions);
            this.shapes.push(rectangle);
        }

        this.render();
    }
}

/**
 * @class Shape
 * @description Base class for all shapes in the 2D modeling tool
 */
class Shape {
    /**
     * @constructor
     * @param {Object} position - The position of the shape
     * @param {Object} options - Configuration options for the shape
     */
    constructor(position, options = {}) {
        this.position = position;
        this.options = {
            strokeColor: options.strokeColor || '#000000',
            fillColor: options.fillColor || '#FFFFFF',
            lineWidth: options.lineWidth || 2,
            ...options
        };
        this.isSelected = false;
    }

    /**
     * @method draw
     * @param {CanvasRenderingContext2D} ctx - The canvas rendering context
     * @description Draw the shape on the canvas (to be implemented by subclasses)
     */
    draw(ctx) {
        throw new Error('draw method must be implemented by subclasses');
    }

    /**
     * @method move
     * @param {Object} newPosition - The new position for the shape
     * @description Move the shape to a new position
     */
    move(newPosition) {
        this.position = newPosition;
    }

    /**
     * @method containsPoint
     * @param {Object} point - The point to check
     * @returns {boolean} True if the shape contains the point, false otherwise
     * @description Check if the shape contains a given point (to be implemented by subclasses)
     */
    containsPoint(point) {
        throw new Error('containsPoint method must be implemented by subclasses');
    }

    /**
     * @method toSVG
     * @returns {string} The SVG representation of the shape
     * @description Convert the shape to an SVG string (to be implemented by subclasses)
     */
    toSVG() {
        throw new Error('toSVG method must be implemented by subclasses');
    }
}

/**
 * @class Rectangle
 * @extends Shape
 * @description Represents a rectangle shape in the 2D modeling tool
 */
class Rectangle extends Shape {
    /**
     * @constructor
     * @param {Object} position - The position of the rectangle
     * @param {Object} dimensions - The dimensions of the rectangle
     * @param {Object} options - Configuration options for the rectangle
     */
    constructor(position, dimensions, options = {}) {
        super(position, options);
        this.dimensions = dimensions;
    }

    /**
     * @method setDimensions
     * @param {Object} dimensions - The new dimensions for the rectangle
     * @description Update the dimensions of the rectangle
     */
    setDimensions(dimensions) {
        this.dimensions = dimensions;
    }

    /**
     * @method draw
     * @param {CanvasRenderingContext2D} ctx - The canvas rendering context
     * @description Draw the rectangle on the canvas
     */
    draw(ctx) {
        ctx.save();
        ctx.strokeStyle = this.options.strokeColor;
        ctx.fillStyle = this.options.fillColor;
        ctx.lineWidth = this.options.lineWidth;

        ctx.beginPath();
        ctx.rect(this.position.x, this.position.y, this.dimensions.width, this.dimensions.height);
        ctx.fill();
        ctx.stroke();

        if (this.isSelected) {
            ctx.strokeStyle = '#0000FF';
            ctx.setLineDash([5, 5]);
            ctx.strokeRect(
                this.position.x - 2,
                this.position.y - 2,
                this.dimensions.width + 4,
                this.dimensions.height + 4
            );
        }

        ctx.restore();
    }

    /**
     * @method containsPoint
     * @param {Object} point - The point to check
     * @returns {boolean} True if the rectangle contains the point, false otherwise
     * @description Check if the rectangle contains a given point
     */
    containsPoint(point) {
        return (
            point.x >= this.position.x &&
            point.x <= this.position.x + this.dimensions.width &&
            point.y >= this.position.y &&
            point.y <= this.position.y + this.dimensions.height
        );
    }

    /**
     * @method toSVG
     * @returns {string} The SVG representation of the rectangle
     * @description Convert the rectangle to an SVG string
     */
    toSVG() {
        return `<rect x="${this.position.x}" y="${this.position.y}" width="${this.dimensions.width}" height="${this.dimensions.height}" 
                fill="${this.options.fillColor}" stroke="${this.options.strokeColor}" stroke-width="${this.options.lineWidth}" />`;
    }
}

// Export the Web2DModeling class for use in other modules
export default Web2DModeling;
