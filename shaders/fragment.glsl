#version 330 core

in vec2 fragmentTexCoord;
flat in int fragmentFace;

uniform sampler2D textureLeft;
uniform sampler2D textureRight;
uniform sampler2D textureTop;

out vec4 color;

void main()
{
    if (fragmentFace == 0)
    {
        color = texture(textureLeft, fragmentTexCoord);
    }
    else if (fragmentFace == 1)
    {
        color = texture(textureRight, fragmentTexCoord);
    }
    else
    {
        color = texture(textureTop, fragmentTexCoord);
    }
}
