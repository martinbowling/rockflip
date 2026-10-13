"""Original three-color explorer actions; source-body16x24, no wildlife handling.
Peek lowers the explorer's head without entering the cover cell. Lift uses a
free hand beside the body (the separately drawn stone transaction owns the rock).
Camera raises the original strapped lens; no camera graphics borrowed from IP.
"""
from PIL import Image
ACTIONS=('peek','lift','camera')
DIRECTIONS=('down','up','right','left')
def poses(player):
    result={}
    for action in ACTIONS:
        for direction in DIRECTIONS:
            source=player[direction+'_a']
            # Author right once and mirror its complete left-handed silhouette.
            if direction=='left':
                for phase in range(2):result[f'{action}_{direction}_{phase}']=[r[::-1] for r in result[f'{action}_right_{phase}']]
                continue
            for phase in range(2):
                g=[list('.'*16) for _ in range(24)]
                if action in ('peek','lift'):
                    lower=2+phase
                    # Hat/face bend toward cover, knees flex; boots remain grounded.
                    for y in range(0,11):
                        for x,c in enumerate(source[y]):g[y+lower][x]=c
                    for y in range(11,19):
                        for x,c in enumerate(source[y]):
                            if c!='.':g[min(21,y+lower)][x]=c
                    for y in range(21,23):g[y]=list(source[y])
                    arm=('...11331........','...13331........','....111.........') if direction=='up' else ('..........11331.','..........13331.','...........111..')
                    ay=16 if action=='peek' else 18-phase*2
                    for n,row in enumerate(arm):
                        for x,c in enumerate(row):
                            if c!='.':g[ay+n][x]=c
                    # A bent knee/open stance, not a lifted or hovering whole-body box.
                    g[20]=list('....12211221....');g[21]=list('...1221..1221...')
                else:
                    g=[list(r) for r in source]
                    if direction=='up':
                        rows=('...1331111331...','...1312222131...','....11233211....','.....111111.....')
                    elif direction=='right':
                        rows=('.......13311111.','.......13123331.','........1123131.','.........111111.')
                    else:
                        rows=('...1331111331...','...1312332131...','....11211311....','.....111111.....')
                    for n,row in enumerate(rows):g[10+phase+n]=list(row)
                    # Original round lens: dark rim, brown glass, one skin-light glint.
                    if direction!='up':
                        cx=12 if direction=='right' else 8;cy=12+phase
                        g[cy][cx]='3';g[cy+1][cx]='2'
                result[f'{action}_{direction}_{phase}']=[''.join(r) for r in g]
    return result

def emit_explorer_actions(outdir,player,palette):
    from pathlib import Path
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    source=poses(player);sheet=Image.new('P',(16*len(source),24),0)
    colors=sum((list(c) for c in palette),[]);sheet.putpalette(colors+[0]*(768-len(colors)))
    for n,(name,grid) in enumerate(source.items()):
        assert len(grid)==24 and all(len(r)==16 for r in grid)
        for y,row in enumerate(grid):
            for x,c in enumerate(row):sheet.putpixel((n*16+x,y),0 if c=='.' else int(c))
    sheet.save(out/'player_actions.png');sheet.resize((sheet.width*4,96),Image.Resampling.NEAREST).save(out/'player_actions_4x.png')
    import json
    (out/'player-actions.json').write_text(json.dumps({'source':'art/src/explorer_actions.py','order':list(source),'body':[16,24],'import_canvas':[16,32],'palette':'ranger','actions':list(ACTIONS),'status':'source_authored_not_native_observed'},indent=2)+'\n')
    return source
