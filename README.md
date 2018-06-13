# Corona Archiver

Python script to help **pack** and **unpack** Corona archive .car file

## Distribution

#### Windows binary (.exe)

https://github.com/0BuRner/corona-archiver/releases

## Usage

#### Unpacking
``` Usage: corona-archiver.py -u 'input_file' 'output_dir' ```

#### Packing
``` Usage: corona-archiver.py -p 'input_dir' 'output_file' ```

## File structure

```
[header]
    [magic_number] (4 bytes) \x72\x61\x63\x01
    [revision] (4 bytes)
    [data_offset_start] (4 bytes)
    [index_size] (4 bytes)

[index]
    [entry]
        [entry_type] (4 bytes) 1
        [data_offset] (4 bytes)
        [filename_length] (4 bytes)
        [filename] (filename_length+1 bytes) 0-terminated
        [padding] (1|2|3|4 bytes) \x00

[data]
    [entry]
        [entry_type] (4 bytes) 2
        [next_data_offset] (4 bytes)
        [file_size] (4 bytes)
        [file_content] (file_size bytes)
        [padding] (0|1|2|3 bytes) \x00

[end]
    [magic_number] (4 bytes) \xFF\xFF\xFF\xFF
    [padding] (4 bytes) \x00
```

## Others languages

Java : https://github.com/zhuowei/Chromosphere/tree/master/carlib

## LUA

### LUA Decompilers 
- https://sourceforge.net/projects/unluac/
- https://github.com/viruscamp/luadec

### LUA Tools
- http://lua-users.org/wiki/LuaTools
