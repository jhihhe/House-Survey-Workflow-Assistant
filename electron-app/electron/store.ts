import Store from 'electron-store';
import path from 'path';
import os from 'os';

// Define the schema for our settings
interface Settings {
  root_dir: string;
  photographer_name: string;
  photo_src: string;
  vr_src: string;
  theme: string;
}

const schema = {
  root_dir: {
    type: 'string',
    default: path.join(os.homedir(), 'Pictures'),
  },
  photographer_name: {
    type: 'string',
    default: '郭艳',
  },
  photo_src: {
    type: 'string',
    default: '',
  },
  vr_src: {
    type: 'string',
    default: '',
  },
  theme: {
    type: 'string',
    default: 'dark',
  },
};

const store = new Store<Settings>({ schema: schema as any });

export default store;
