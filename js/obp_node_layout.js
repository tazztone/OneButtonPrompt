import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "OneButtonPrompt.Layout",
    async nodeCreated(node) {
        if (node.comfyClass === "OneButtonPreset") {
            const advancedWidgets = [
                "descriptor_density",
                "body_type_chance",
                "outfit_chance",
                "hair_chance",
                "accessory_chance",
                "face_detail_chance",
                "expression_chance",
                "pose_chance",
                "background_chance",
                "mood_chance",
                "lighting_chance",
                "color_scheme_chance",
                "lens_chance",
                "shot_size_chance",
                "art_movement_chance",
                "quality_chance",
                "save_preset_name",
                "prompt_prefix_mode",
                "prompt_suffix_mode",
                "custom_wildcard_1",
                "custom_wildcard_1_chance",
                "custom_wildcard_2",
                "custom_wildcard_2_chance",
                "custom_wildcard_3",
                "custom_wildcard_3_chance",
                "custom_wildcard_4",
                "custom_wildcard_4_chance"
            ];

            const toggleWidgetName = "show_advanced";

            const updateVisibility = (show) => {
                let changed = false;
                if (!node.widgets) return;

                for (const w of node.widgets) {
                    if (advancedWidgets.includes(w.name)) {
                        // Store original type if not already stored
                        if (!w.origType) {
                            w.origType = w.type;
                            w.origComputeSize = w.computeSize;
                        }

                        // Determine target type
                        const targetType = show ? w.origType : "hidden";

                        if (w.type !== targetType) {
                            w.type = targetType;
                            // For hidden widgets, we might need to suppress size computation
                            if (!show) {
                                w.computeSize = () => [0, -4]; // Shrink vertical space
                            } else {
                                w.computeSize = w.origComputeSize;
                            }
                            changed = true;
                        }
                    }
                }

                if (changed) {
                    node.setSize(node.computeSize());
                    node.setDirtyCanvas(true, true);
                }
            };

            // Find the toggle widget
            const toggleWidget = node.widgets.find(w => w.name === toggleWidgetName);
            if (toggleWidget) {
                // Hook callback
                const originalCallback = toggleWidget.callback;
                toggleWidget.callback = function (value) {
                    updateVisibility(value);
                    if (originalCallback) {
                        return originalCallback.apply(this, arguments);
                    }
                };

                // Initialize state (default hidden)
                // We use setTimeout to ensure all widgets are fully initialized
                setTimeout(() => {
                    updateVisibility(toggleWidget.value);
                }, 100);
            } else {
                console.warn("[OneButtonPrompt.Layout] Could not find show_advanced widget.");
            }
        }
    }
});
