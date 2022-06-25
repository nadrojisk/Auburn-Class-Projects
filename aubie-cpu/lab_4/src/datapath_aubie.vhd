-- Author Jordan Sosnowski
-- Lab 4 (CPU) for Computer Architecture

-- entity reg_file (lab 2)
use work.dlx_types.all;
use work.bv_arithmetic.all;

entity reg_file is
    generic(prop_delay : Time := 5 ns);
    port (
        data_in     :   in dlx_word;
        readnotwrite:   in bit;
        clock       :   in bit;
	data_out    :   out dlx_word;
        reg_number  :   in register_index
    );
end entity reg_file;


architecture behavior of reg_file is
		type reg_type is array (0 to 31) of dlx_word;
begin
	reg_file_process: process(readnotwrite, clock, reg_number, data_in) is
		variable registers: reg_type;
	begin
		-- Start process
		if (clock = '1') then
			if (readnotwrite = '1') then
				data_out <= registers(bv_to_integer(reg_number)) after prop_delay;
			else
				registers(bv_to_integer(reg_number)) := data_in;

			end if;
		end if;
	end process reg_file_process;
end architecture behavior;


-- entity alu (lab 3)
use work.dlx_types.all;
use work.bv_arithmetic.all;

entity alu is
    generic(prop_delay : Time := 5 ns);
    port(
        operand1  :   in dlx_word;
        operand2  :   in dlx_word;
        operation :   in alu_operation_code;
        result    :   out dlx_word;
        error     :   out error_code
    );
end entity alu;

-- alu_operation_code values
-- 0000 unsigned add
-- 0001 signed add
-- 0010 2's compl add
-- 0011 2's compl sub
-- 0100 2's compl mul
-- 0101 2's compl divide
-- 0110 logical and
-- 0111 bitwise and
-- 1000 logical or
-- 1001 bitwise or
-- 1010 logical not (op1)
-- 1011 bitwise not (op1)
-- 1101-1111 output all zeros

-- error code values
-- 0000 = no error
-- 0001 = overflow (too big positive)
-- 0010 = underflow (too small neagative)
-- 0011 = divide by zero

architecture behavior of ALU is
    -- Define any types here that will be used

begin
    alu_process: process(operand1, operand2, operation) is
          -- Declare any local variables here
          variable temp_result: dlx_word := x"00000000";
          variable logical_true: dlx_word := x"00000001";
          variable logical_false: dlx_word := x"00000000";
          variable overflow_flag_set: boolean;
          variable div_by_zero: boolean;
          variable op1_logical_status: bit; -- 0 means false; 1 means true
          variable op2_logical_status: bit; -- 0 means false; 1 means true

          begin
              error <= "0000"; -- Default value for port signal output error
              case(operation) is
                  when "0000" => -- UNSIGNED ADD
                      bv_addu(operand1, operand2, temp_result, overflow_flag_set);
                      if overflow_flag_set then
                          error <= "0001";
                      end if;
                      result <= temp_result;
                  when "0001" => -- UNSIGNED SUBTRACT
                      bv_subu(operand1, operand2, temp_result, overflow_flag_set);
                      if overflow_flag_set then
                          error <= "0010";
                          -- Unsigned subtract is only concerned with underflow
                      end if;
                      result <= temp_result;
                  when "0010" => -- TWO'S COMPLEMENT ADD
                      bv_add(operand1, operand2, temp_result, overflow_flag_set);
                      if overflow_flag_set then
                          -- IF (+A) + (+B) = -C
                          if (operand1(31) = '0') AND (operand2(31) = '0') then
                              if (temp_result(31) = '1') then
                                  error <= "0001"; -- overflow occurred
                              end if;
                          -- (-A) + (-B) = +C
                          elsif (operand1(31) = '1') AND (operand2(31) = '1') then
                              if (temp_result(31) = '0') then
                                  error <= "0010"; -- underflow occurred
                              end if;
                          end if;
                      end if;
                      result <= temp_result;
                  when "0011" => -- TWO'S COMPLEMENT SUBTRACT
                      bv_sub(operand1, operand2, temp_result, overflow_flag_set);
                      if overflow_flag_set then
                          -- IF (-A) - (+B) = +C
                          if (operand1(31) = '1') AND (operand2(31) = '0') then
                              if (temp_result(31) = '0') then
                                  error <= "0010"; -- underflow occurred
                              end if;
                          -- IF (+A) - (-B) = -C
                          elsif (operand1(31) = '0') AND (operand2(31) = '1') then
                              if (temp_result(31) = '1') then
                                  error <= "0001"; -- overflow occurred
                              end if;
                          end if;
                      end if;
                      result <= temp_result;
                  when "0100" => -- TWO'S COMPLEMENT MULTIPLY - (2 underflow Conditions + 2 overflow conditions)
                      bv_mult(operand1, operand2, temp_result, overflow_flag_set);
                      if overflow_flag_set then
                          if (operand1(31) = '1') AND (operand2(31) = '0') then -- (-A x +B) = +C
                              error <= "0010"; -- underflow
                          elsif (operand1(31) = '0') AND (operand2(31) = '1') then -- (+A x -B) = +C
                              error <= "0010"; -- underflow
                          else -- (+A x +B) = -C OR (-A x -B) = -C
                              error <= "0001"; -- overflow
                          end if;
                      end if;
                      result <= temp_result;
                  when "0101" => -- TWO'S COMPLEMENT DIVIDE
                      bv_div(operand1, operand2, temp_result, div_by_zero, overflow_flag_set);
                      if div_by_zero then
                          error <= "0011"; --
                      elsif overflow_flag_set then
                          error <= "0010"; -- only an underflow can occur with divide (see note above)
                      end if;
                      result <= temp_result;
                  when "0110" => -- PERFORM LOGICAL AND
                      op1_logical_status := '0'; -- Default logical status for operand1
                      op2_logical_status := '0'; -- Default logical status for operand2
                      -- check if operand1 is a non-zero value --
                      for i in 31 downto 0 loop
                          -- If non-zero value, operand1 is logical true;
                          if (operand1(i) = '1') then
                              op1_logical_status := '1';
                              exit;
                          end if;
                      end loop;
                      -- check if operand2 is a non-zero value
                      for i in 31 downto 0 loop
                          -- If non-zero value, operand2 is logical true;
                          if (operand2(i) = '1') then
                              op2_logical_status := '1';
                              exit;
                          end if;
                      end loop;
                      -- IF operand statuses result in --> '1' && '1' = '1'
                      if ((op1_logical_status AND op2_logical_status) = '1') then
                          result <= logical_true; -- The result is logical true x"00000001"
                      else
                          result <= logical_false; -- Else result is logical false  x"00000000"
                      end if;
                  when "0111" => -- PERFORM BITWISE AND
                      for i in 31 downto 0 loop
                          temp_result(i) := operand1(i) AND operand2(i);
                      end loop;
                      result <= temp_result;
                  when "1000" => -- PERFORM LOGICAL OR
                      op1_logical_status := '0'; -- Default logical status for operand 1
                      op2_logical_status := '0'; -- Default logical status for operand 2
                      -- check if operand1 is a non-zero value --
                      for i in 31 downto 0 loop
                          -- If non-zero value, operand1 is logical true;
                          if (operand1(i) = '1') then
                              op1_logical_status := '1';
                              exit;
                          end if;
                      end loop;
                      -- check if operand2 is a non-zero value
                      for i in 31 downto 0 loop
                          -- If non-zero value, operand2 is logical true;
                          if (operand2(i) = '1') then
                              op2_logical_status := '1';
                              exit;
                          end if;
                      end loop;
                      -- IF operand statuses result in --> ('1'||'1' OR '1'||'0' OR '0'||'1' ) = '1'
                      if ((op1_logical_status OR op2_logical_status) = '1') then
                          result <= logical_true; -- The result is logical true x"00000001"
                      else
                          result <= logical_false; -- Else result is logical false  x"00000000"
                      end if;
                  when "1001" => -- PERFORM BITWISE OR
                      for i in 31 downto 0 loop
                          temp_result(i) := operand1(i) OR operand2(i);
                      end loop;
                      result <= temp_result;
                  when "1010" => -- PERFORM LOGICAL NOT OF OPERAND1 (ignore operand2)
                      temp_result := logical_true; -- Initially assigned to true (i.e. 32'h00000001)
                      for i in 31 downto 0 loop
                          if (NOT operand1(i) = '0') then -- i.e. IF operand1 is non-zero
                              temp_result := logical_false; -- logical NOT resulted in false; Therefore, NOT(operand1) = false
                              exit;
                          end if;
                      end loop;
                      result <= temp_result;
                  when "1011" => -- PERFORM BITWISE NOT OF OPERAND1 (ignore operand2)
                      for i in 31 downto 0 loop
                          temp_result(i) := NOT operand1(i);
                      end loop;
                      result <= temp_result;
                  when "1100" => -- CHECK IF OPERAND1 is zero
                      temp_result := logical_false;
                      if (operand1 = x"00000000") then
                          temp_result := logical_true;
                      end if;
                      result <= temp_result;
                  when others => -- 1101 thru 1111 outputs all zeroes
                      result <= x"00000000";
              end case;
   end process alu_process;
end architecture behavior;

-- entity dlx_register (lab 3)
use work.dlx_types.all;

entity dlx_register is
    generic(prop_delay : Time := 5 ns);
    port(
        in_val  :   in dlx_word;
        clock   :   in bit;
        out_val :   out dlx_word
    );
end entity dlx_register;


architecture behavior of dlx_register is

begin
	dlx_reg_process: process(in_val, clock) is
	begin
		-- Start process
		if (clock = '1') then
			out_val <= in_val after prop_delay;
		end if;
	end process dlx_reg_process;
end architecture behavior;

-- entity pcplusone
use work.dlx_types.all;
use work.bv_arithmetic.all;

entity pcplusone is
	generic(prop_delay: Time := 5 ns);
	port (
        input : in dlx_word;
        clock : in bit;
        output: out dlx_word
    );
end entity pcplusone;

architecture behavior of pcplusone is
begin
    plusone: process(input, clock) is  -- add clock input to make it execute
        variable newpc: dlx_word;
        variable error: boolean;
    begin
        if clock'event and clock = '1' then
            bv_addu(input,"00000000000000000000000000000001",newpc,error);
            output <= newpc after prop_delay;
        end if;
    end process plusone;
end architecture behavior;


-- entity mux
use work.dlx_types.all;

entity mux is
     generic(prop_delay : Time := 5 ns);
     port (
            input_1 : in dlx_word;
            input_0 : in dlx_word;
            which   : in bit;
            output  : out dlx_word
     );
end entity mux;

architecture behavior of mux is
begin
   muxProcess : process(input_1, input_0, which) is
   begin
      if (which = '1') then
         output <= input_1 after prop_delay;
      else
         output <= input_0 after prop_delay;
      end if;
   end process muxProcess;
end architecture behavior;
-- end entity mux

-- entity threeway_mux
use work.dlx_types.all;

entity threeway_mux is
    generic(prop_delay : Time := 5 ns);
    port (
        input_2 : in dlx_word;
        input_1 : in dlx_word;
        input_0 : in dlx_word;
        which   : in threeway_muxcode;
        output  : out dlx_word
    );
end entity threeway_mux;

architecture behavior of threeway_mux is
begin
   muxProcess : process(input_1, input_0, which) is
   begin
      if (which = "10" or which = "11" ) then
         output <= input_2 after prop_delay;
      elsif (which = "01") then
         output <= input_1 after prop_delay;
      else
         output <= input_0 after prop_delay;
      end if;
   end process muxProcess;
end architecture behavior;
-- end entity mux


-- entity memory
use work.dlx_types.all;
use work.bv_arithmetic.all;

entity memory is
    port (
        address       :   in dlx_word;
        readnotwrite  :   in bit;
        data_out      :   out dlx_word;
        data_in       :   in dlx_word;
        clock         :   in bit
    );
end memory;

architecture behavior of memory is

begin  -- behavior

    mem_behav: process(address,clock) is
    -- note that there is storage only for the first 1k of the memory, to speed
    -- up the simulation
        type memtype is array (0 to 1024) of dlx_word;
        variable data_memory : memtype;
    begin
    -- fill this in by hand to put some values in there
    -- some instructions
        data_memory(0) :=  X"30200000"; --LD R4, 0x100
        data_memory(1) :=  X"00000100"; -- address 0x100 for previous instruction
        -- R4 = Contents of Mem Addr x100 = x"5500FF00"

        data_memory(2) :=  X"30080000"; -- LD R1, 0x101
        data_memory(3) :=  X"00000101"; -- address 0x101 for previous instruction
        -- R1 = Contents of Mem Addd x101 = x"AA00FF00"


        data_memory(4) :=  X"30100000"; -- LD R2, 0x102 = 258
        data_memory(5) :=  X"00000102"; -- address 0x102 for previous instruction
        -- R2 = Contents of Mem Addr x102 = x"00000001"

        data_memory(6) :=  "00000000000110000100010000000000"; -- ADDU R3,R1, R2
        -- R3 = Contents of (R1 + R2) = x"AA00FF01"

        data_memory(7) :=  "00100000000000001100000000000000"; -- STO R3, 0x103
        data_memory(8) :=  x"00000103"; -- address 0x103 for previous instruction
        -- Mem Addr x"103" = data_memory(259) := contents of R3 = x"AA00FF01"


        data_memory(9) :=  "00110001000000000000000000000000"; -- LDI R0, 0x104
        data_memory(10) := x"00000104"; -- #Imm value 0x104 for previous instruction
        -- Contents of R0 = x"00000104"

        data_memory(11) := "00100010000000001100000000000000"; -- STOR (R0), R3
        -- Contents of Mem Addr specifed by R0 (x104 = 260) = Contents of R3 = x"AA00FF01"

        data_memory(12) := "00110010001010000000000000000000"; -- LDR R5, (R0)
        -- Contents of R5 = Contents specified by Mem Addr[Contents of R0] = x"AA00FF01"

        data_memory(13) := x"40000000"; -- JMP to 261 = x"105"
        data_memory(14) := x"00000105"; -- Address to jump to for previous instruction
        -- JMP to Mem Addr x"105" is an Add Operation --> SUBU R11, R1, R2 => Contents of R11 = x"AA00FEFF"

        -- note that this code runs every time an input signal to memory changes,
        -- so for testing, write to some other locations besides these
        data_memory(256) := "01010101000000001111111100000000"; -- x"100" = 256
        data_memory(257) := "10101010000000001111111100000000"; -- x"101" = 257
        data_memory(258) := "00000000000000000000000000000001"; -- x"102" = 258

        -- We Jumped here from Addr 14 = x"0000000E"
        data_memory(261) :=  x"01584400"; -- SUBU R11,R1,R2

        data_memory(262) := x"4101C000"; -- JZ R7, 267 = x"10B" -- If R7 == 0, GOTO Addr 267
        data_memory(263) := x"0000010B"; -- Address to jump to for previous instruction
        -- JZ to Mem Addr x"10B" is an Add Operation --> SUBU R12, R1, R2 => Contents of R12 = x"AA00FEFF"

        -- We jumped here from Addr 263 = x"00000107"
        data_memory(267) := x"01604400"; -- SUBU R12, R1, R2

        data_memory(268) := x"10000000"; -- NOOP


        if clock = '1' then
          if readnotwrite = '1' then
            -- do a read
            data_out <= data_memory(bv_to_natural(address)) after 5 ns;
          else
            -- do a write
            data_memory(bv_to_natural(address)) := data_in;
          end if;
        end if;
  end process mem_behav;
end behavior;
-- end entity memory
