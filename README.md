![GitHub Release](https://img.shields.io/github/v/release/0burner/corona-archiver)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-pr/0burner/corona-archiver)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/0burner/corona-archiver/total) 

# Corona Archiver | Solar2D Game Engine pack/unpack

Python script to help **pack** and **unpack** Corona archive .car file

## Distribution

#### Windows binary (.exe)

https://github.com/0BuRner/corona-archiver/releases

## Usage

#### Unpacking
``` Usage: corona-archiver.py -u 'input_file' 'output_dir' ```

```example: corona-archiver.py -u /home/0burner/resources.car /home/0burner/decompiled/```

#### Packing
``` Usage: corona-archiver.py -p 'input_dir' 'output_file' ```

```example: corona-archiver.py -p /home/0burner/decompiled/ /home/0burner/new_recompiled.car```

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

- C++ (official implementation) : https://github.com/coronalabs/corona/blob/master/librtt/Rtt_Archive.cpp
- Java : https://github.com/zhuowei/Chromosphere/tree/master/carlib

## LUA

### LUA Decompilers 
- https://www.decompiler.com/
- https://sourceforge.net/projects/unluac/
- https://github.com/sztupy/luadec51 (Lua 5.1)
- https://github.com/viruscamp/luadec (Lua 5.2, 5.3)

### LUA Tools
- http://lua-users.org/wiki/LuaTools

## Tutorials

### Dissasembling
- https://medium.com/@ngocnv73/disassembling-a-compiled-lua-module-using-a-questionable-method-f1a38f25fa4a
- https://platinmods.com/threads/solar2d-former-corona-lab-game-modding-tutorial.121378/ (dissasembling + recompiling)
- https://gameguardian.net/forum/topic/19033-day-r-survival/page/43/#comment-135978
- https://code.hmil.fr/2015/02/00-hacking-funrun2-how-to-reverse-engineer-a-corona-app/
