from typing import Dict, Any, List, Tuple

class LoraChain:
    """
    一个用于在 ComfyUI 工作流中便捷叠加 LoRA 的助手类。
    支持链式调用，自动管理节点 ID 和连接逻辑。
    """
    def __init__(self, base_model_id: str, base_clip_id: str, start_node_id: int = 100):
        self.current_model = [base_model_id, 0]
        self.current_clip = [base_clip_id, 0]
        self.nodes = {}
        self.next_id = start_node_id

    def add_lora(self, lora_name: str, strength_model: float = 1.0, strength_clip: float = 1.0) -> 'LoraChain':
        """
        叠加一个新的 LoRA 节点。
        """
        node_id = str(self.next_id)
        self.nodes[node_id] = {
            "inputs": {
                "lora_name": lora_name,
                "strength_model": strength_model,
                "strength_clip": strength_clip,
                "model": self.current_model,
                "clip": self.current_clip
            },
            "class_type": "LoraLoader"
        }
        
        # 更新当前的输出引用
        self.current_model = [node_id, 0]
        self.current_clip = [node_id, 1]
        self.next_id += 1
        return self

    def get_nodes(self) -> Dict[str, Any]:
        """获取生成的 LoRA 节点字典"""
        return self.nodes

    def get_final_targets(self) -> Tuple[List[Any], List[Any]]:
        """获取最终叠加完 LoRA 后的 model 和 clip 引用"""
        return self.current_model, self.current_clip

def apply_loras_to_prompt(prompt: Dict[str, Any], lora_list: List[Dict[str, Any]], 
                         model_node_id: str = "4", clip_node_id: str = "4") -> Dict[str, Any]:
    """
    工具函数：将一组 LoRA 配置自动注入到现有的 prompt JSON 中。
    """
    if not lora_list:
        return prompt

    chain = LoraChain(model_node_id, clip_node_id)
    for lora in lora_list:
        chain.add_lora(
            lora['name'], 
            lora.get('strength_model', 1.0), 
            lora.get('strength_clip', 1.0)
        )
    
    # 合并节点
    new_nodes = chain.get_nodes()
    prompt.update(new_nodes)
    
    # 更新后续节点对 model 和 clip 的引用
    final_model, final_clip = chain.get_final_targets()
    
    for node in prompt.values():
        if "inputs" in node:
            inputs = node["inputs"]
            for key, value in inputs.items():
                if isinstance(value, list) and len(value) >= 1:
                    if value[0] == model_node_id:
                        inputs[key] = final_model
                    elif value[0] == clip_node_id:
                        inputs[key] = final_clip
                        
    return prompt
