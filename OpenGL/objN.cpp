
// objN.cpp - Object creation and management for Fork 3D modeling software
// Copyright (c) 2023 Fork Software Inc. All rights reserved.
// made with openGL. 

#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <vector>
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>
#include <memory>
#include <algorithm>
#include <random>
#include <chrono>
#include <thread>
#include <mutex>
#include <atomic>
#include <condition_variable>
#include <future>

// Custom headers
#include "shader.h"
#include "camera.h"
#include "texture.h"
#include "material.h"
#include "light.h"
#include "mesh.h"
#include "scene.h"
#include "utils.h"
#include "config.h"
#include "logger.h"

// Constants
const unsigned int SCR_WIDTH = 1920;
const unsigned int SCR_HEIGHT = 1080;
const float PI = 3.14159265358979323846f;

// Global variables
std::atomic<bool> g_isRunning(true);
std::mutex g_mutex;
std::condition_variable g_cv;

// Forward declarations
class Object3D;
class Primitive;
class Cube;
class Sphere;
class Cylinder;
class Cone;
class Torus;

// Utility function declarations
glm::vec3 generateRandomColor();
std::string getUniqueObjectName(const std::string& baseName);
void logCreationInfo(const std::string& objectType, const std::string& objectName);

// Object3D class definition
class Object3D {
public:
    Object3D(const std::string& name) : m_name(name), m_position(0.0f), m_rotation(0.0f), m_scale(1.0f) {
        m_id = generateUniqueId();
        logCreationInfo("Object3D", m_name);
    }

    virtual ~Object3D() = default;

    virtual void render(const Shader& shader) const = 0;
    virtual void update(float deltaTime) = 0;

    void setPosition(const glm::vec3& position) { m_position = position; }
    void setRotation(const glm::vec3& rotation) { m_rotation = rotation; }
    void setScale(const glm::vec3& scale) { m_scale = scale; }

    glm::vec3 getPosition() const { return m_position; }
    glm::vec3 getRotation() const { return m_rotation; }
    glm::vec3 getScale() const { return m_scale; }
    std::string getName() const { return m_name; }
    unsigned int getId() const { return m_id; }

protected:
    std::string m_name;
    unsigned int m_id;
    glm::vec3 m_position;
    glm::vec3 m_rotation;
    glm::vec3 m_scale;
    std::vector<GLfloat> m_vertices;
    std::vector<GLuint> m_indices;
    GLuint m_vao, m_vbo, m_ebo;

    virtual void setupMesh() {
        glGenVertexArrays(1, &m_vao);
        glGenBuffers(1, &m_vbo);
        glGenBuffers(1, &m_ebo);

        glBindVertexArray(m_vao);
        glBindBuffer(GL_ARRAY_BUFFER, m_vbo);
        glBufferData(GL_ARRAY_BUFFER, m_vertices.size() * sizeof(GLfloat), m_vertices.data(), GL_STATIC_DRAW);

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, m_ebo);
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, m_indices.size() * sizeof(GLuint), m_indices.data(), GL_STATIC_DRAW);

        // Vertex positions
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), (void*)0);
        // Vertex normals
        glEnableVertexAttribArray(1);
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), (void*)(3 * sizeof(GLfloat)));
        // Vertex texture coords
        glEnableVertexAttribArray(2);
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), (void*)(6 * sizeof(GLfloat)));

        glBindVertexArray(0);
    }

private:
    static unsigned int generateUniqueId() {
        static unsigned int nextId = 0;
        return nextId++;
    }
};

// Primitive class definition
class Primitive : public Object3D {
public:
    Primitive(const std::string& name) : Object3D(name), m_material(std::make_shared<Material>()) {
        m_material->setAmbient(generateRandomColor());
        m_material->setDiffuse(generateRandomColor());
        m_material->setSpecular(glm::vec3(0.5f));
        m_material->setShininess(32.0f);
    }

    void render(const Shader& shader) const override {
        shader.use();

        glm::mat4 model = glm::mat4(1.0f);
        model = glm::translate(model, m_position);
        model = glm::rotate(model, glm::radians(m_rotation.x), glm::vec3(1.0f, 0.0f, 0.0f));
        model = glm::rotate(model, glm::radians(m_rotation.y), glm::vec3(0.0f, 1.0f, 0.0f));
        model = glm::rotate(model, glm::radians(m_rotation.z), glm::vec3(0.0f, 0.0f, 1.0f));
        model = glm::scale(model, m_scale);

        shader.setMat4("model", model);
        shader.setVec3("material.ambient", m_material->getAmbient());
        shader.setVec3("material.diffuse", m_material->getDiffuse());
        shader.setVec3("material.specular", m_material->getSpecular());
        shader.setFloat("material.shininess", m_material->getShininess());

        glBindVertexArray(m_vao);
        glDrawElements(GL_TRIANGLES, static_cast<GLsizei>(m_indices.size()), GL_UNSIGNED_INT, 0);
        glBindVertexArray(0);
    }

    void update(float deltaTime) override {
        // Implement any necessary updates for the primitive object
    }

    void setMaterial(const std::shared_ptr<Material>& material) { m_material = material; }
    std::shared_ptr<Material> getMaterial() const { return m_material; }

protected:
    std::shared_ptr<Material> m_material;
};

// Cube class definition
class Cube : public Primitive {
public:
    Cube(const std::string& name, float size = 1.0f) : Primitive(name) {
        logCreationInfo("Cube", name);
        generateCubeGeometry(size);
        setupMesh();
    }

private:
    void generateCubeGeometry(float size) {
        float halfSize = size / 2.0f;

        m_vertices = {
            // positions          // normals           // texture coords
            -halfSize, -halfSize, -halfSize,  0.0f,  0.0f, -1.0f,  0.0f, 0.0f,
             halfSize, -halfSize, -halfSize,  0.0f,  0.0f, -1.0f,  1.0f, 0.0f,
             halfSize,  halfSize, -halfSize,  0.0f,  0.0f, -1.0f,  1.0f, 1.0f,
            -halfSize,  halfSize, -halfSize,  0.0f,  0.0f, -1.0f,  0.0f, 1.0f,

            -halfSize, -halfSize,  halfSize,  0.0f,  0.0f,  1.0f,  0.0f, 0.0f,
             halfSize, -halfSize,  halfSize,  0.0f,  0.0f,  1.0f,  1.0f, 0.0f,
             halfSize,  halfSize,  halfSize,  0.0f,  0.0f,  1.0f,  1.0f, 1.0f,
            -halfSize,  halfSize,  halfSize,  0.0f,  0.0f,  1.0f,  0.0f, 1.0f,

            -halfSize,  halfSize,  halfSize, -1.0f,  0.0f,  0.0f,  1.0f, 0.0f,
            -halfSize,  halfSize, -halfSize, -1.0f,  0.0f,  0.0f,  1.0f, 1.0f,
            -halfSize, -halfSize, -halfSize, -1.0f,  0.0f,  0.0f,  0.0f, 1.0f,
            -halfSize, -halfSize,  halfSize, -1.0f,  0.0f,  0.0f,  0.0f, 0.0f,

             halfSize,  halfSize,  halfSize,  1.0f,  0.0f,  0.0f,  1.0f, 0.0f,
             halfSize,  halfSize, -halfSize,  1.0f,  0.0f,  0.0f,  1.0f, 1.0f,
             halfSize, -halfSize, -halfSize,  1.0f,  0.0f,  0.0f,  0.0f, 1.0f,
             halfSize, -halfSize,  halfSize,  1.0f,  0.0f,  0.0f,  0.0f, 0.0f,

            -halfSize, -halfSize, -halfSize,  0.0f, -1.0f,  0.0f,  0.0f, 1.0f,
             halfSize, -halfSize, -halfSize,  0.0f, -1.0f,  0.0f,  1.0f, 1.0f,
             halfSize, -halfSize,  halfSize,  0.0f, -1.0f,  0.0f,  1.0f, 0.0f,
            -halfSize, -halfSize,  halfSize,  0.0f, -1.0f,  0.0f,  0.0f, 0.0f,

            -halfSize,  halfSize, -halfSize,  0.0f,  1.0f,  0.0f,  0.0f, 1.0f,
             halfSize,  halfSize, -halfSize,  0.0f,  1.0f,  0.0f,  1.0f, 1.0f,
             halfSize,  halfSize,  halfSize,  0.0f,  1.0f,  0.0f,  1.0f, 0.0f,
            -halfSize,  halfSize,  halfSize,  0.0f,  1.0f,  0.0f,  0.0f, 0.0f
        };

        m_indices = {
             0,  1,  2,  2,  3,  0,
             4,  5,  6,  6,  7,  4,
             8,  9, 10, 10, 11,  8,
            12, 13, 14, 14, 15, 12,
            16, 17, 18, 18, 19, 16,
            20, 21, 22, 22, 23, 20
        };
    }
};

// Sphere class definition
class Sphere : public Primitive {
public:
    Sphere(const std::string& name, float radius = 1.0f, unsigned int rings = 32, unsigned int sectors = 32)
        : Primitive(name), m_radius(radius), m_rings(rings), m_sectors(sectors) {
        logCreationInfo("Sphere", name);
        generateSphereGeometry();
        setupMesh();
    }

private:
    float m_radius;
    unsigned int m_rings;
    unsigned int m_sectors;

    void generateSphereGeometry() {
        float const R = 1.0f / static_cast<float>(m_rings - 1);
        float const S = 1.0f / static_cast<float>(m_sectors - 1);

        for (unsigned int r = 0; r < m_rings; ++r) {
            for (unsigned int s = 0; s < m_sectors; ++s) {
                float const y = std::sin(-PI / 2 + PI * r * R);
                float const x = std::cos(2 * PI * s * S) * std::sin(PI * r * R);
                float const z = std::sin(2 * PI * s * S) * std::sin(PI * r * R);

                m_vertices.push_back(x * m_radius);
                m_vertices.push_back(y * m_radius);
                m_vertices.push_back(z * m_radius);

                m_vertices.push_back(x);
                m_vertices.push_back(y);
                m_vertices.push_back(z);

                m_vertices.push_back(s * S);
                m_vertices.push_back(r * R);
            }
        }

        for (unsigned int r = 0; r < m_rings - 1; ++r) {
            for (unsigned int s = 0; s < m_sectors - 1; ++s) {
                m_indices.push_back(r * m_sectors + s);
                m_indices.push_back(r * m_sectors + (s + 1));
                m_indices.push_back((r + 1) * m_sectors + (s + 1));

                m_indices.push_back(r * m_sectors + s);
                m_indices.push_back((r + 1) * m_sectors + (s + 1));
                m_indices.push_back((r + 1) * m_sectors + s);
            }
        }
    }
};

// Cylinder class definition
class Cylinder : public Primitive {
public:
    Cylinder(const std::string& name, float radius = 1.0f, float height = 2.0f, unsigned int sectors = 32)
        : Primitive(name), m_radius(radius), m_height(height), m_sectors(sectors) {
        logCreationInfo("Cylinder", name);
        generateCylinderGeometry();
        setupMesh();
    }

private:
    float m_radius;
    float m_height;
    unsigned int m_sectors;

    void generateCylinderGeometry() {
        float const S = 1.0f / static_cast<float>(m_sectors)
    }}