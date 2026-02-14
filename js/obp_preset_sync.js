import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "OneButtonPrompt.PresetSync",
    async nodeCreated(node) {
        if (node.comfyClass === "OneButtonPreset") {
            const presetWidget = node.widgets.find(w => w.name === "OneButtonPreset");

            // Map of internal preset keys to slider widget names
            // Keys must match the keys in the preset JSON
            const sliderMap = {
                "outfitchance": "outfit_chance",
                "hairchance": "hair_chance",
                "accessorychance": "accessory_chance",
                "buildfacechance": "face_detail_chance",
                "humanexpressionchance": "expression_chance",
                "posechance": "pose_chance",
                "humanoidbackgroundchance": "background_chance",
                "moodchance": "mood_chance",
                "lightingchance": "lighting_chance",
                "colorschemechance": "color_scheme_chance",
                "lenschance": "lens_chance",
                "shotsizechance": "shot_size_chance",
                "artmovementchance": "art_movement_chance",
                "subjectbodytypechance": "body_type_chance",
            };

            // Reverse tier mapping (name -> int)
            const tiers = ["never", "novel", "extraordinary", "unique", "legendary", "rare", "uncommon", "normal", "common", "always"];

            // Function to update sliders
            const updateSliders = async (presetName) => {
                try {
                    const response = await api.fetchApi(`/one_button_prompt/get_preset?name=${encodeURIComponent(presetName)}`);
                    if (response.status !== 200) return;

                    const data = await response.json();

                    // Iterate and update
                    for (const [key, widgetName] of Object.entries(sliderMap)) {
                        const widget = node.widgets.find(w => w.name === widgetName);
                        if (widget) {
                            // If key exists in preset, map it. Else set to -1 (default)
                            if (data[key]) {
                                const val = tiers.indexOf(data[key]);
                                if (val !== -1) {
                                    widget.value = val;
                                } else {
                                    widget.value = -1;
                                }
                            } else {
                                widget.value = -1;
                            }
                        }
                    }

                    // Special cases if any (e.g. descriptor density which maps to 2 keys)
                    // descriptor_density checks subjectdescriptor1chance usually.
                    const densityWidget = node.widgets.find(w => w.name === "descriptor_density");
                    if (densityWidget) {
                        if (data["subjectdescriptor1chance"]) {
                            const val = tiers.indexOf(data["subjectdescriptor1chance"]);
                            if (val !== -1) densityWidget.value = val;
                        } else {
                            densityWidget.value = -1;
                        }
                    }
                    const qualityWidget = node.widgets.find(w => w.name === "quality_chance");
                    if (qualityWidget) {
                        if (data["quality1chance"]) {
                            const val = tiers.indexOf(data["quality1chance"]);
                            if (val !== -1) qualityWidget.value = val;
                        } else {
                            qualityWidget.value = -1;
                        }
                    }


                    node.setDirtyCanvas(true, true);

                } catch (error) {
                    console.error("OBP Preset Sync Error:", error);
                }
            };

            // Initial Sync
            // We want to sync on load, but we also don't want to overwrite user's saved workflow values if they loaded a workflow.
            // However, the user request "ideally when i select a preset" implies an active action.
            // So we settle for only on change.

            // Hook into callback
            // ComfyUI widgets usually have a 'callback' property
            if (presetWidget) {
                const originalCallback = presetWidget.callback;
                presetWidget.callback = function (value) {
                    updateSliders(value);
                    if (originalCallback) {
                        return originalCallback.apply(this, arguments);
                    }
                };
            }
        }
    }
});
