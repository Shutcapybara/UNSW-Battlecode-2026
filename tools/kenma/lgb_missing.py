"""Lane-local adapter: LightGBM missing_type=None treats a NaN feature as zero."""
import export_gbt
import lightgbm as lgb

def from_lgb(path):
    packed=export_gbt.from_lgb(path)
    dump=lgb.Booster(model_file=path).dump_model()
    counts=dict(none_nodes=0,changed_nan_routes=0)
    for nodes,tree in zip(packed['trees'],dump['tree_info']):
        index=0
        def visit(n):
            nonlocal index
            i=index;index+=1
            if 'leaf_value' in n:
                assert nodes[i][0]=='L';return
            assert nodes[i][0]=='N' and nodes[i][1]==n['split_feature']
            if n['missing_type']=='None':
                counts['none_nodes']+=1
                route=0.0<=n['threshold']
                counts['changed_nan_routes']+=route!=nodes[i][3]
                nodes[i][3]=route
            visit(n['left_child']);visit(n['right_child'])
        visit(tree['tree_structure']);assert index==len(nodes)
    return packed,counts
