importScripts("https://cdn.jsdelivr.net/pyodide/v0.23.0/full/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/1.2.0/dist/wheels/bokeh-3.2.0-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.2.0/dist/wheels/panel-1.2.0-py3-none-any.whl', 'pyodide-http==0.2.1', 'context_manager', 'pandas']
  for (const pkg of env_spec) {
    let pkg_name;
    if (pkg.endsWith('.whl')) {
      pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    } else {
      pkg_name = pkg
    }
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    try {
      await self.pyodide.runPythonAsync(`
        import micropip
        await micropip.install('${pkg}');
      `);
    } catch(e) {
      console.log(e)
      self.postMessage({
	type: 'status',
	msg: `Error while installing ${pkg_name}`
      });
    }
  }
  console.log("Packages loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  
import asyncio

from panel.io.pyodide import init_doc, write_doc

init_doc()

import pandas as pd
import panel as pn
from context_manager import ContextManager

pn.extension('tabulator', template='material')

def load_data():
    df1 = pd.read_csv('data_ingestion/data/cards.csv')
    df2 = pd.read_csv('data_ingestion/data/cards_rings_db_info.csv')

    df2.rename(columns={
        'type_name': 'type',
        'sphere_name': 'sphere',
        'pack_name': 'pack',
    }, inplace=True)
    df3 = df2.merge(df1, on=['name', 'type', 'sphere', 'pack'], how='left')

    df3.rename(columns={
        'quantity_x': 'quantity_in_pack',
        'quantity_y': 'quantity_in_collection',
    }, inplace=True)

    df3 = df3[[
        'name',
        'sphere',
        'pack',
        'quantity_in_pack', 
        'quantity_in_collection',
        'imagesrc'
    ]]
    
    return df3

df = load_data()
cm = ContextManager(df)

name_search = pn.widgets.AutocompleteInput(
    name='Search for a card by name:', 
    options=df.name.unique().tolist(),
    placeholder='Card name...',
    case_sensitive=False
)
name_search.param.watch(cm.name_search_handler, 'value_input')

sphere_selection = pn.widgets.RadioBoxGroup(
    name='Select a sphere:',
    options=['all']+df.sphere.unique().tolist(),
    inline=True,
    button_type='primary',
)
sphere_selection.param.watch(cm.sphere_selection_handler, 'value')

collection_select = pn.widgets.Switch(
    value= True
)
collection_select.param.watch(cm.collection_select_handler, 'value')
collection_select = pn.Row(
    'Show only cards in collection:',
    collection_select
)
sphere_and_collection_select = pn.Column(sphere_selection, collection_select)

pn.Column(
    pn.Row(name_search, sphere_and_collection_select),
    pn.Row(cm.df_widget, cm.box),
).servable()



await write_doc()
  `

  try {
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
    self.postMessage({
      type: 'render',
      docs_json: docs_json,
      render_items: render_items,
      root_ids: root_ids
    })
  } catch(e) {
    const traceback = `${e}`
    const tblines = traceback.split('\n')
    self.postMessage({
      type: 'status',
      msg: tblines[tblines.length-2]
    });
    throw e
  }
}

self.onmessage = async (event) => {
  const msg = event.data
  if (msg.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    from panel.io.state import state
    from panel.io.pyodide import _link_docs_worker

    _link_docs_worker(state.curdoc, sendPatch, setter='js')
    `)
  } else if (msg.type === 'patch') {
    self.pyodide.globals.set('patch', msg.patch)
    self.pyodide.runPythonAsync(`
    state.curdoc.apply_json_patch(patch.to_py(), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.globals.set('location', msg.location)
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads(location)
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()