<p float="left">
  <img src="example/result.png" width="90%" />
</p>

&nbsp;

# Key Parameters

- `--prompt`: Main description for the thumbnail image (**required**)
- `--negative_prompt`: Elements to avoid in generation  
_(default: `""`)_
- `--width`: Width of the generated image  
_(default: `1280`)_
- `--height`: Height of the generated image  
_(default: `720`)_
- `--seed`: Seed for reproducible generation  
_(default: `-1` for random)_

---

# Usage Example

```bash
cog predict \
-i prompt="Modern YouTube thumbnail with bold text 'AI REVOLUTION' in neon colors, split screen showing before/after transformation, cyberpunk aesthetic with electric blue and purple highlights" \
-i negative_prompt="blurry, low quality, text artifacts" \
-i width=1280 \
-i height=720 \
-i seed=12345