#version 330 core

layout (location = 0) in vec3 vertexData;
layout (location = 1) in vec2 vertexTexCoord;

uniform float warpLeft[8];
uniform float warpRight[8];
uniform float warpTop[8];

out vec2 fragmentTexCoord;
flat out int fragmentFace;

void main()
{
    float x = vertexData.x;
    float y = vertexData.y;
    int face = int(vertexData.z + 0.5);

    float u = x;
    float v = y;

    if (face == 0)
    {
        float d = warpLeft[6] * x + warpLeft[7] * y + 1.0;
        u = (warpLeft[0] * x + warpLeft[1] * y + warpLeft[2]) / d;
        v = (warpLeft[3] * x + warpLeft[4] * y + warpLeft[5]) / d;
    }
    else if (face == 1)
    {
        float d = warpRight[6] * x + warpRight[7] * y + 1.0;
        u = (warpRight[0] * x + warpRight[1] * y + warpRight[2]) / d;
        v = (warpRight[3] * x + warpRight[4] * y + warpRight[5]) / d;
    }
    else
    {
        float d = warpTop[6] * x + warpTop[7] * y + 1.0;
        u = (warpTop[0] * x + warpTop[1] * y + warpTop[2]) / d;
        v = (warpTop[3] * x + warpTop[4] * y + warpTop[5]) / d;
    }

    gl_Position = vec4(u, v, 0.0, 1.0);
    fragmentTexCoord = vertexTexCoord;
    fragmentFace = face;
}
